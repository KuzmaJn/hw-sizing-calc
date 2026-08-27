from dataclasses import dataclass


@dataclass
class TransactionProfile:
    name: str
    description: str
    cpu_ms_per_tx: float
    ram_mb_per_tx: float
    storage_kb_per_tx: float


@dataclass
class SizingDefaults:
    cpu_utilization_target: float
    safety_margin: float
    retention_days: int
    concurrency_factor: float


@dataclass
class SizingResult:
    cpu_cores: int
    ram_gb: int
    disk_gb: int
    assumptions: dict
