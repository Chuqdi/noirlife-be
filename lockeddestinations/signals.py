from datetime import timedelta

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import LockedDestination
from .tasks import (
    send_scheduled_destination_notification,
    send_prepare_to_return_notification,
    send_return_check_15,
    send_return_check_30,
    send_final_return_check,
)

# Adjust this import to wherever your project's Celery app instance lives,
# e.g. `from config.celery import app as celery_app`.
from BE.celery import app as celery_app


# =========================================================================
# Scheduled trip start notification (unchanged from before)
# =========================================================================

@receiver(post_save, sender=LockedDestination)
def schedule_destination_notification(sender, instance: LockedDestination, created, **kwargs):
    """
    On creation of a SCHEDULED LockedDestination, schedule a Celery task
    (via ETA) to fire a push notification at scheduled_time.

    Only runs on creation — LockedDestination gets saved repeatedly later
    (arrived_at, left_at, drifted_at updates from location tracking), and
    we don't want those updates to re-trigger scheduling.
    """
    if not created:
        return

    if instance.schedule_type != LockedDestination.Status.SCHEDULED:
        return

    if not instance.scheduled_time:
        return

    if instance.scheduled_time <= timezone.now():
        return

    result = send_scheduled_destination_notification.apply_async(
        args=[instance.id],
        eta=instance.scheduled_time,
    )

    # .update() bypasses .save(), so this does NOT re-trigger post_save —
    # avoids recursively calling this signal again.
    LockedDestination.objects.filter(id=instance.id).update(
        notification_task_id=result.id
    )


@receiver(post_save, sender=LockedDestination)
def revoke_cancelled_destination_notification(sender, instance: LockedDestination, created, **kwargs):
    """
    If a scheduled destination gets cancelled before its scheduled_time
    arrives, revoke the pending Celery task so the notification never fires.
    """
    if created:
        return

    if not instance.is_cancelled:
        return

    if not instance.notification_task_id:
        return

    celery_app.control.revoke(instance.notification_task_id)

    LockedDestination.objects.filter(id=instance.id).update(
        notification_task_id=None
    )


# =========================================================================
# Return check-in tasks (prepare / check_15 / check_30 / check_45)
# Scheduled/rescheduled off expected_return_time, independent of the
# scheduled-trip-start logic above.
# =========================================================================

CHECKIN_OFFSETS = {
    "prepare": timedelta(minutes=-5),
    "check_15": timedelta(minutes=15),
    "check_30": timedelta(minutes=30),
    "check_45": timedelta(minutes=45),
}

CHECKIN_TASKS = {
    "prepare": send_prepare_to_return_notification,
    "check_15": send_return_check_15,
    "check_30": send_return_check_30,
    "check_45": send_final_return_check,
}


def _revoke_checkin_tasks(instance: LockedDestination):
    task_ids = instance.checkin_task_ids or {}
    for task_id in task_ids.values():
        if task_id:
            celery_app.control.revoke(task_id)

    if task_ids:
        LockedDestination.objects.filter(id=instance.id).update(checkin_task_ids={})


def _schedule_checkin_tasks(instance: LockedDestination):
    now = timezone.now()
    new_ids = {}

    for key, offset in CHECKIN_OFFSETS.items():
        eta = instance.expected_return_time + offset
        if eta <= now:
            # This particular checkpoint has already passed — skip just
            # this one, still schedule whichever others are still future.
            continue

        task_fn = CHECKIN_TASKS[key]
        result = task_fn.apply_async(args=[instance.id], eta=eta)
        new_ids[key] = result.id

    LockedDestination.objects.filter(id=instance.id).update(checkin_task_ids=new_ids)


@receiver(pre_save, sender=LockedDestination)
def cache_old_expected_return_time(sender, instance: LockedDestination, **kwargs):
    """Stash the previous expected_return_time so post_save can detect changes."""
    if not instance.pk:
        instance._old_expected_return_time = None
        return

    instance._old_expected_return_time = (
        LockedDestination.objects.filter(pk=instance.pk)
        .values_list("expected_return_time", flat=True)
        .first()
    )


@receiver(post_save, sender=LockedDestination)
def manage_checkin_tasks(sender, instance: LockedDestination, created, **kwargs):
    old_value = getattr(instance, "_old_expected_return_time", None)

    # Cancelled trips should never have pending return check-ins.
    if instance.is_cancelled:
        _revoke_checkin_tasks(instance)
        return

    if not instance.expected_return_time:
        # No return time set (or it was cleared) — revoke any leftovers.
        if instance.checkin_task_ids:
            _revoke_checkin_tasks(instance)
        return

    if instance.expected_return_time != old_value:
        # New or changed return time — replace any previously scheduled
        # check-ins with fresh ones for the new time.
        _revoke_checkin_tasks(instance)
        _schedule_checkin_tasks(instance)