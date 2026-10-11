"""Registry of optional external schedule providers."""

from __future__ import annotations

from typing import Any

from .provider import ExternalScheduleProvider
from .ramses_cc import RamsesCcScheduleProvider


def build_provider_registry(hass: Any) -> dict[str, ExternalScheduleProvider]:
    """Build supported providers without importing them from Velair core."""
    provider = RamsesCcScheduleProvider(hass)
    return {provider.key: provider}
