"""Geopolitical features - placeholder.

The GDELT- and WGI-backed implementations were removed for refactoring
(see checklist Section 12/13). This stub preserves the public API surface so
the feature registry and discovery pipeline keep working while the source is
rebuilt. All feature methods raise ``NotImplementedError``.
"""

from typing import Literal


class geopolitical_features:
    def __init__(self, os_api: str):
        self._os_api = os_api

    def _unimplemented(self):
        raise NotImplementedError("geopolitical features are stubbed pending GDELT/WGI source rebuild")

    def conflict_event_count_30d(self, country_code: str, mode: Literal["F", "ML"] = "F") -> int:
        return self._unimplemented()

    def conflict_event_count_90d(self, country_code: str, mode: Literal["F", "ML"] = "F") -> int:
        return self._unimplemented()

    def conflict_trend(self, country_code: str, mode: Literal["F", "ML"] = "F") -> str:
        return self._unimplemented()

    def goldstein_scale_avg_30d(self, country_code: str, mode: Literal["F", "ML"] = "F") -> float:
        return self._unimplemented()

    def goldstein_scale_trend(self, country_code: str, mode: Literal["F", "ML"] = "F") -> float:
        return self._unimplemented()

    def battle_deaths_30d(self, country_code: str, mode: Literal["F", "ML"] = "F") -> int:
        return self._unimplemented()

    def battle_deaths_90d(self, country_code: str, mode: Literal["F", "ML"] = "F") -> int:
        return self._unimplemented()

    def protest_event_count_30d(self, country_code: str, mode: Literal["F", "ML"] = "F") -> int:
        return self._unimplemented()

    def protest_violence_level(self, country_code: str, mode: Literal["F", "ML"] = "F") -> float:
        return self._unimplemented()

    def diplomatic_event_count_30d(self, country_code: str, mode: Literal["F", "ML"] = "F") -> int:
        return self._unimplemented()

    def diplomatic_intensity_avg(self, country_code: str, mode: Literal["F", "ML"] = "F") -> float:
        return self._unimplemented()

    def sanctions_count_active(self, country_code: str, mode: str = "F") -> int:
        return self._unimplemented()

    def sanctions_new_30d(self, country_code: str, mode: str = "F") -> int:
        return self._unimplemented()

    def sanctions_sector_coverage(self, country_code: str, mode: str = "F") -> float:
        return self._unimplemented()

    def governance_wgi_composite(self, country_code: str, mode: Literal["F", "ML"] = "F") -> float:
        return self._unimplemented()

    def corruption_perception_index(self, country_code: str, mode: str = "F") -> int:
        return self._unimplemented()

    def rule_of_law_score(self, country_code: str, mode: Literal["F", "ML"] = "F") -> float:
        return self._unimplemented()

    def regulatory_quality(self, country_code: str, mode: Literal["F", "ML"] = "F") -> float:
        return self._unimplemented()

    def democracy_index(self, country_code: str, mode: str = "F") -> float:
        return self._unimplemented()

    def regime_type(self, country_code: str, mode: str = "F") -> Literal["democracy", "hybrid", "autocracy"]:
        return self._unimplemented()

    def press_freedom_score(self, country_code: str, mode: str = "F") -> int:
        return self._unimplemented()


__all__ = ["geopolitical_features"]
