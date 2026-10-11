"""Contract implemented by external schedule providers."""

from __future__ import annotations

from typing import Any, Protocol

from .models import ExternalScheduleCapabilities


class ExternalScheduleProvider(Protocol):
    """Provider boundary; publication receives a scheduler-resolved week."""

    key: str
    capabilities: ExternalScheduleCapabilities

    def compatible_entities(self, managed_entities: list[str]) -> list[str]: ...

    async def async_publish(
        self,
        entity_id: str,
        schedule: dict[str, list[dict[str, Any]]],
        temperature_unit: str,
    ) -> None: ...
