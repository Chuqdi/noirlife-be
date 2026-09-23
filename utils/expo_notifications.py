"""
Send push notifications via Expo's push API.

Usage:
    from push_notifications import send_push_notification, send_push_notifications_bulk

    send_push_notification(
        token=user.expo_push_token,
        title="Your ride is arriving",
        body="Tap to track your driver",
        data={"url": "yourapp://ride/123/track"},
    )
"""

import logging
from dataclasses import dataclass, field
from typing import Any

import requests

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
EXPO_PUSH_RECEIPTS_URL = "https://exp.host/--/api/v2/push/getReceipts"
MAX_BATCH_SIZE = 100  # Expo's hard limit per request


@dataclass
class PushMessage:
    token: str
    title: str
    body: str
    data: dict[str, Any] = field(default_factory=dict)
    sound: str | None = "default"
    channel_id: str | None = None  # Android notification channel
    badge: int | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "to": self.token,
            "title": self.title,
            "body": self.body,
            "data": self.data,
        }
        if self.sound is not None:
            payload["sound"] = self.sound
        if self.channel_id is not None:
            payload["channelId"] = self.channel_id
        if self.badge is not None:
            payload["badge"] = self.badge
        return payload


def _is_valid_expo_token(token: str) -> bool:
    return bool(token) and (
        token.startswith("ExponentPushToken[") or token.startswith("ExpoPushToken[")
    )


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
    sound: str | None = "default",
    channel_id: str | None = None,
) -> dict[str, Any] | None:
    """Send a single push notification. Returns the Expo ticket, or None if skipped."""
    if not _is_valid_expo_token(token):
        logger.warning("Skipping push: invalid Expo token %r", token)
        return None

    message = PushMessage(
        token=token, title=title, body=body, data=data or {}, sound=sound, channel_id=channel_id
    )
    result = send_push_notifications_bulk([message])
    return result[0] if result else None


def send_push_notifications_bulk(messages: list[PushMessage]) -> list[dict[str, Any]]:
    """
    Send up to many push messages, automatically chunked into batches of 100
    (Expo's per-request limit). Returns the list of tickets from Expo, in order.

    Each ticket has a "status" of "ok" or "error". A ticket status of "ok" does
    NOT guarantee delivery — check receipts separately (see check_push_receipts)
    to catch invalid/unregistered device tokens.
    """
    valid_messages = [m for m in messages if _is_valid_expo_token(m.token)]
    skipped = len(messages) - len(valid_messages)
    if skipped:
        logger.warning("Skipping %d push message(s) with invalid tokens", skipped)

    all_tickets: list[dict[str, Any]] = []

    for i in range(0, len(valid_messages), MAX_BATCH_SIZE):
        batch = valid_messages[i : i + MAX_BATCH_SIZE]
        payload = [m.to_payload() for m in batch]

        try:
            response = requests.post(
                EXPO_PUSH_URL,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            tickets = response.json().get("data", [])
            all_tickets.extend(tickets)

            for msg, ticket in zip(batch, tickets):
                if ticket.get("status") == "error":
                    logger.error(
                        "Push failed for token %s: %s (%s)",
                        msg.token,
                        ticket.get("message"),
                        ticket.get("details", {}).get("error"),
                    )
        except requests.RequestException:
            logger.exception("Expo push request failed for a batch of %d message(s)", len(batch))

    return all_tickets


def check_push_receipts(ticket_ids: list[str]) -> dict[str, Any]:
    """
    Check delivery receipts for previously sent tickets (call this ~15+ minutes
    after sending). Use this to catch DeviceNotRegistered errors and clear out
    stale tokens from your DB.
    """
    receipts: dict[str, Any] = {}

    for i in range(0, len(ticket_ids), MAX_BATCH_SIZE):
        batch = ticket_ids[i : i + MAX_BATCH_SIZE]
        try:
            response = requests.post(
                EXPO_PUSH_RECEIPTS_URL,
                json={"ids": batch},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            batch_receipts = response.json().get("data", {})
            receipts.update(batch_receipts)

            for ticket_id, receipt in batch_receipts.items():
                if receipt.get("status") == "error":
                    error_code = receipt.get("details", {}).get("error")
                    if error_code == "DeviceNotRegistered":
                        logger.info(
                            "Ticket %s: device unregistered — remove this token from your DB",
                            ticket_id,
                        )
                    else:
                        logger.error("Ticket %s failed: %s", ticket_id, receipt.get("message"))
        except requests.RequestException:
            logger.exception("Failed to fetch receipts for a batch of %d ticket(s)", len(batch))

    return receipts