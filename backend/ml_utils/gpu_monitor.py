"""GPU monitoring via pynvml (NVIDIA) with graceful CPU-only fallback."""

from typing import Any, Dict, Optional

from backend import config


class GPUMonitor:
    def __init__(self) -> None:
        self._nvml = None
        self._handle = None
        self._count = 0
        if config.VLLM_ENABLED:
            return
        try:
            import pynvml  # type: ignore

            pynvml.nvmlInit()
            self._nvml = pynvml
            self._count = pynvml.nvmlDeviceGetCount()
            if self._count > 0:
                self._handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except Exception:
            self._nvml = None
            self._handle = None

    @property
    def available(self) -> bool:
        return self._handle is not None

    def snapshot(self) -> Dict[str, Any]:
        if not self.available:
            return {
                "available": False,
                "vram_usage_mb": 0.0,
                "vram_total_mb": 0.0,
                "gpu_utilization_percent": 0.0,
                "gpu_temperature_c": 0.0,
                "device_count": 0,
            }
        nv = self._nvml
        mem = nv.nvmlDeviceGetMemoryInfo(self._handle)
        util = nv.nvmlDeviceGetUtilizationRates(self._handle)
        temp = nv.nvmlDeviceGetTemperature(
            self._handle, nv.NVML_TEMPERATURE_GPU
        )
        return {
            "available": True,
            "vram_usage_mb": round(mem.used / (1024 * 1024), 1),
            "vram_total_mb": round(mem.total / (1024 * 1024), 1),
            "gpu_utilization_percent": float(util.gpu),
            "gpu_temperature_c": float(temp),
            "device_count": self._count,
        }

    def close(self) -> None:
        if self._nvml is not None:
            try:
                self._nvml.nvmlShutdown()
            except Exception:
                pass