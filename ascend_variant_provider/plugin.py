from __future__ import annotations

import os
from dataclasses import dataclass
from functools import cache
from typing import Protocol, runtime_checkable

from ascend_variant_provider.detect_cann import AscendEnvironment


@runtime_checkable
class VariantPropertyType(Protocol):
    @property
    def namespace(self) -> str: ...
    @property
    def feature(self) -> str: ...
    @property
    def value(self) -> str: ...


@dataclass(frozen=True)
class VariantFeatureConfig:
    name: str
    values: list[str]
    multi_value: bool = False


class AscendVariantFeatureKey:
    NPU_TYPE = "npu_type"
    DRIVER_VERSION = "driver_version"
    CANN_VERSION = "cann_version"

class AscendVariantPlugin:
    namespace = "ascend"
    dynamic = False

    @classmethod
    @cache
    def get_supported_configs(cls, context=None) -> list[VariantFeatureConfig]:
        keyconfigs: list[VariantFeatureConfig] = []
        env = AscendEnvironment.from_system()

        npu_type = os.environ.get("ASCEND_VARIANT_PROVIDER_FORCE_NPU_TYPE")
        if npu_type:
            keyconfigs.append(
                VariantFeatureConfig(
                    name=AscendVariantFeatureKey.NPU_TYPE,
                    values=[npu_type],
                    multi_value=False
                )
            )
        else:
            keyconfigs.append(
                VariantFeatureConfig(
                    name=AscendVariantFeatureKey.NPU_TYPE,
                    values=[npu_type for _, npu_type in (env.npu_types if env else [])],
                    multi_value=True
                )
            )

        driver_version = os.environ.get("ASCEND_VARIANT_PROVIDER_FORCE_DRIVER_VERSION")
        if driver_version:
            keyconfigs.append(
                VariantFeatureConfig(
                    name=AscendVariantFeatureKey.DRIVER_VERSION,
                    values=[driver_version],
                    multi_value=False
                )
            )
        else:
            keyconfigs.append(
                VariantFeatureConfig(
                    name=AscendVariantFeatureKey.DRIVER_VERSION,
                    values=[f"{env.driver_version.major}.{env.driver_version.minor}" + 
                                (f".{env.driver_version.patch}" if env.driver_version and env.driver_version.patch is not None else "") + 
                                (f".rc{env.driver_version.rc}" if env.driver_version and env.driver_version.rc is not None else "")] 
                                if env and env.driver_version else [],
                    multi_value=False
                )
            )

        cann_version = os.environ.get("ASCEND_VARIANT_PROVIDER_FORCE_CANN_VERSION")
        if cann_version:
            keyconfigs.append(
                VariantFeatureConfig(
                    name=AscendVariantFeatureKey.CANN_VERSION,
                    values=[cann_version],
                    multi_value=False
                )
            )
        else:
            keyconfigs.append(
                VariantFeatureConfig(
                    name=AscendVariantFeatureKey.CANN_VERSION,
                    values=[f"{env.cann_version.major}.{env.cann_version.minor}" + 
                                (f".{env.cann_version.patch}" if env.cann_version and env.cann_version.patch is not None else "") + 
                                (f".rc{env.cann_version.rc}" if env.cann_version and env.cann_version.rc is not None else "")] 
                                if env and env.cann_version else [],
                    multi_value=False
                )
            )
        
        return keyconfigs

    @classmethod
    @cache
    def get_all_configs(cls, context=None) -> list[VariantFeatureConfig]:
        return cls.get_supported_configs()
