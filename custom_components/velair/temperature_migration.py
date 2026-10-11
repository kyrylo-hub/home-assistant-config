"""User notification helpers for temperature-data migration."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def notification_id(entry_id: str) -> str:
    """Return the stable persistent-notification identifier for one entry."""
    return f"{DOMAIN}_temperature_migration_{entry_id}"


async def async_notify_temperature_migration(
    hass: HomeAssistant,
    entry_id: str,
    reason: str | None = None,
) -> None:
    """Notify the user that scheduling is blocked pending migration."""
    try:
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "notification_id": notification_id(entry_id),
                "title": (
                    "Velair reset required"
                    if reason == "legacy_celsius_upgrade_reset_required"
                    else "Velair temperature unit changed"
                ),
                "message": (
                    (
                        "This Velair version found published legacy Celsius data while "
                        "Home Assistant uses Fahrenheit. The scheduler has stopped. "
                        "[Open Velair](/velair) and use Reset Velair to create safe "
                        "Fahrenheit defaults."
                    )
                    if reason == "legacy_celsius_upgrade_reset_required"
                    else (
                        "Home Assistant now uses a different temperature unit from "
                        "Velair's stored data. The scheduler has stopped to avoid applying "
                        "incorrect targets. [Open Velair](/velair), review the change, "
                        "and migrate all stored temperatures to the current unit."
                    )
                ),
            },
            blocking=True,
        )
    except Exception:  # Home Assistant service availability must not weaken the block.
        _LOGGER.exception("Unable to create the Velair temperature migration notification")


async def async_dismiss_temperature_migration_notification(
    hass: HomeAssistant,
    entry_id: str,
) -> None:
    """Dismiss a resolved temperature migration notification."""
    try:
        await hass.services.async_call(
            "persistent_notification",
            "dismiss",
            {"notification_id": notification_id(entry_id)},
            blocking=True,
        )
    except Exception:  # A stale notice is safer than preventing scheduler recovery.
        _LOGGER.exception("Unable to dismiss the Velair temperature migration notification")
