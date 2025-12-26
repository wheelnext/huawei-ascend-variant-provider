# Copyright (c) 2025 Huawei Technologies Co., Ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import functools
from dataclasses import dataclass
from functools import lru_cache

from huawei_ascend_variant_provider.pysmi import CannVersion, DriverVersion
from huawei_ascend_variant_provider.pysmi import get_npu_types, get_driver_version, get_cann_version

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