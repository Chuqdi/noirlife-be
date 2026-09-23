from celery import shared_task
from utils.expo_notifications import send_push_notification


def _get_lock_or_none(locked_destination_id: int):
    """Shared fetch helper — local import avoids circular imports at app load."""
    from .models import LockedDestination

    try:
        return LockedDestination.objects.select_related("user").get(id=locked_destination_id)
    except LockedDestination.DoesNotExist:
        return None


def _is_still_pending_return(lock) -> bool:
    """
    True if this trip is still active and the user hasn't returned yet —
    i.e. not cancelled and left_at hasn't been set. This is the only signal
    available at task-fire time since these tasks don't carry a live
    location ping; it relies on left_at being set by your location tracker.
    """
    return not lock.is_cancelled and lock.left_at is None


# --- Scheduled trip start notification (fires at scheduled_time) ---

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_destination_notification(self, locked_destination_id: int):
    lock = _get_lock_or_none(locked_destination_id)
    if lock is None:
        return
    if lock.is_cancelled or lock.is_completed:
        return
    if not lock.user.notification_token:
        return

    send_push_notification(
        token=lock.user.notification_token,
        title="Scheduled trip starting",
        body=f"Your scheduled trip to {lock.destination_name} is starting now.",
    )


# --- Return check-in tasks (fire relative to expected_return_time) ---

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_prepare_to_return_notification(self, locked_destination_id: int):
    """Fires 5 minutes BEFORE expected_return_time."""
    lock = _get_lock_or_none(locked_destination_id)
    if lock is None or not _is_still_pending_return(lock):
        return
    if not lock.user.notification_token:
        return

    send_push_notification(
        token=lock.user.notification_token,
        title="Time to start heading back",
        body=f"Your expected return time from {lock.destination_name} is coming up soon.",
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_return_check_15(self, locked_destination_id: int):
    """Fires 15 minutes AFTER expected_return_time."""
    lock = _get_lock_or_none(locked_destination_id)
    if lock is None or not _is_still_pending_return(lock):
        return
    if not lock.user.notification_token:
        return

    send_push_notification(
        token=lock.user.notification_token,
        title="Still at your destination?",
        body=f"It's past your expected return time from {lock.destination_name}. Time to head home.",
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_return_check_30(self, locked_destination_id: int):
    """Fires 30 minutes AFTER expected_return_time."""
    lock = _get_lock_or_none(locked_destination_id)
    if lock is None or not _is_still_pending_return(lock):
        return
    if not lock.user.notification_token:
        return

    send_push_notification(
        token=lock.user.notification_token,
        title="Reminder: head home soon",
        body=f"You're 30 minutes past your expected return time from {lock.destination_name}.",
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_final_return_check(self, locked_destination_id: int):
    """
    Fires 45 minutes AFTER expected_return_time. If the user still hasn't
    returned, warns them their Trust Circle is being notified, then
    triggers that notification.
    """
    lock = _get_lock_or_none(locked_destination_id)
    if lock is None or not _is_still_pending_return(lock):
        return

    if lock.user.notification_token:
        send_push_notification(
            token=lock.user.notification_token,
            title="Your Trust Circle is being notified",
            body=f"You haven't checked in from {lock.destination_name}. We're letting your Trust Circle know.",
        )

    notify_trust_circle.delay(locked_destination_id)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_trust_circle(self, locked_destination_id: int):
    """
    Placeholder — Trust Circle functionality isn't built yet. Wire this up
    once Trust Circle contacts/model exist (e.g. fetch the user's trusted
    contacts and push/SMS them with the lock's destination + last known
    location).
    """
    pass