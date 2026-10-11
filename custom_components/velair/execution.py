"""Execution ownership guard for managed climate entities."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ExternalExecutionError(ValueError):
    """Raised when Velair is asked to control an externally owned climate."""


class ExecutionAuthority:
    """Resolve the persisted execution owner without provider knowledge."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        # Keep the stable storage root, not only its current zones mapping:
        # portable imports can replace data["zones"] atomically.
        self._data = data
        self._forced_external: set[str] = set()

    def _zones(self) -> Mapping[str, dict[str, Any]]:
        zones = self._data.get("zones")
        if isinstance(zones, Mapping):
            return zones
        # Backwards-compatible convenience for focused tests and callers that
        # provide the zones mapping directly.
        return self._data  # type: ignore[return-value]

    def is_external(self, entity_id: str) -> bool:
        """Return whether physical execution belongs to an external system."""
        if entity_id in self._forced_external:
            return True
        execution = self._zones().get(entity_id, {}).get("execution")
        return isinstance(execution, dict) and execution.get("type") == "external"

    def hold_external(self, entity_id: str) -> None:
        """Keep the physical-action barrier closed during an ownership change."""
        self._forced_external.add(entity_id)

    def release_external(self, entity_id: str) -> None:
        """Release a temporary ownership-change barrier."""
        self._forced_external.discard(entity_id)

    def ensure_local(self, entity_id: str) -> None:
        """Reject direct physical control for externally owned entities."""
        if self.is_external(entity_id):
            raise ExternalExecutionError(
                f"{entity_id} is executed by an external system; Velair climate "
                "actions are inactive"
            )
