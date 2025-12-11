import sys
import os
import re
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


_CANN_VERSION_REGEX = re.compile(r"version="
                                 r"(?P<major>\d+)"
                                 r"\.(?P<minor>\d+)"
                                 r"(?:\.(?P<patch>\d+))?"
                                 r"(?:\.RC(?P<rc>\d+))?"
                                 r"(?:\.(?P<stage>alpha|beta)(?P<stage_ver>\d+))?", re.MULTILINE)

_DRIVER_VERSION_REGEX = re.compile(r"Version:"
                                   r"\s*(?P<major>\d+)"
                                   r"\.(?P<minor>\d+)"
                                   r"(?:\.(?P<patch>\d+))?"
                                   r"(?:\.rc(?P<rc>\d+))?", re.MULTILINE)

_NPU_TYPE_REGEX = re.compile(r"^\|\s*(?P<index>\d+)\s+(?P<npu>\d+[A-Za-z]+)\d*\s+\|", re.MULTILINE)

# Currently only have major/minor/patch versions, but might want to add more version identifiers in the future
@dataclass(frozen=True)
class CannVersion:
    major: int = 0
    minor: int = 0
    patch: Optional[int] = None
    rc: Optional[int] = None

@dataclass(frozen=True)
class DriverVersion:
    major: int = 0
    minor: int = 0
    patch: Optional[int] = None
    rc: Optional[int] = None
    stage: Optional[str] = None
    stage_ver: Optional[int] = None

class AscendSmiError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

def get_npu_types() -> List[tuple[int, str]]:
    npu_smi_path = shutil.which("npu-smi")
    if npu_smi_path is None:
        raise AscendSmiError("npu-smi command not found in PATH")
    try:
        result = subprocess.run(
            ["npu-smi", "info"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

    except subprocess.TimeoutExpired as exc:
        raise AscendSmiError("npu-smi info timed out") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise AscendSmiError(f"npu-smi info failed: {stderr or exc}") from exc

    npu_types: List[tuple[int, str]] = []
    for match in _NPU_TYPE_REGEX.finditer(result.stdout):
        if match:
            npu_index = int(match.group("index"))
            npu_type = match.group("npu").strip().lower()
            npu_types.append((npu_index, npu_type))
            logger.info(f"Detected NPU type: index={npu_index}, type={npu_type}")

    if not npu_types:
        logger.warning("unable to parse NPU types from npu-smi output")
        raise AscendSmiError("unable to parse NPU types from npu-smi output")

    return npu_types

def get_driver_version() -> Optional[DriverVersion]:
    npu_smi_path = shutil.which("npu-smi")
    if npu_smi_path is None:
        raise AscendSmiError("npu-smi command not found in PATH")
    try:
        result = subprocess.run(
            ["npu-smi", "info"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

    except subprocess.TimeoutExpired as exc:
        raise AscendSmiError("npu-smi info timed out") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise AscendSmiError(f"npu-smi info failed: {stderr or exc}") from exc

    match = _DRIVER_VERSION_REGEX.search(result.stdout)
    if match:
        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch")) if match.group("patch") is not None else None
        rc = int(match.group("rc")) if match.group("rc") is not None else None
        logger.info(f"Detected driver version: {major}.{minor}" + (f".{patch}" if patch is not None else "") + (f".rc{rc}" if rc is not None else ""))
        return DriverVersion(major=major, minor=minor, patch=patch, rc=rc)

    logger.warning("unable to parse driver version from npu-smi output")
    return None

def get_cann_version() -> Optional[CannVersion]:
    cann_path = os.environ.get("ASCEND_TOOLKIT_HOME")
    if cann_path is None:
        logger.warning("ASCEND_TOOLKIT_HOME environment variable not set")
        return None

    arch = os.uname().machine
    version_file = os.path.join(cann_path, f"{arch}-linux", "ascend_toolkit_install.info")
    
    if not os.path.isfile(version_file):
        logger.warning(f"CANN version file not found: {version_file}")
        return None

    with open(version_file, "r") as f:
        content = f.read()
        match = _CANN_VERSION_REGEX.search(content)
        if match:
            major = int(match.group("major"))
            minor = int(match.group("minor"))
            patch = int(match.group("patch")) if match.group("patch") is not None else None
            rc = int(match.group("rc")) if match.group("rc") is not None else None
            logger.info(f"Detected CANN version: {major}.{minor}" + (f".{patch}" if patch is not None else "") + (f".RC{rc}" if rc is not None else "") + (f".{match.group('stage')}{match.group('stage_ver')}" if match.group("stage") and match.group("stage_ver") else ""))
            return CannVersion(major=major, minor=minor, patch=patch, rc=rc)

    logger.warning("unable to parse CANN version from version file")
    return None
    