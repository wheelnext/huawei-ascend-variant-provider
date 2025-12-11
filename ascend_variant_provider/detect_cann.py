from __future__ import annotations

import functools
from dataclasses import dataclass
from functools import lru_cache

from ascend_variant_provider.pysmi import CannVersion, DriverVersion
from ascend_variant_provider.pysmi import get_npu_types, get_driver_version, get_cann_version

@dataclass(frozen=True)
class AscendEnvironment:
    driver_version: Optional[DriverVersion]
    cann_version: Optional[CannVersion]
    npu_types: List[tuple[int, str]]

    @classmethod
    @lru_cache(maxsize=1)
    def from_system(cls) -> AscendEnvironment | None:
        try:
            npu_types = get_npu_types()
            driver_version = get_driver_version()
            cann_version = get_cann_version()

            return cls(
                driver_version=driver_version,
                cann_version=cann_version,
                npu_types=npu_types
            )
        except Exception as e:
            print(f"AscendEnvironment.from_system: failed to detect Ascend environment: {e}")
            return None

if __name__ == "__main__":
    print(f"{AscendEnvironment.from_system()=}")