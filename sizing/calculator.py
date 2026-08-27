import math

from sizing.models import TransactionProfile, SizingDefaults, SizingResult

SECONDS_PER_DAY = 86400
BYTES_PER_GB = 1024 * 1024  # storage_kb_per_tx is in KB, so KB -> GB


def _round_up_to_power_of_two(value: float) -> int:
    """Round RAM up to the next 'sane' allocatable size (1, 2, 4, 8, 16...)."""
    if value <= 1:
        return 1
    return 2 ** math.ceil(math.log2(value))


def calculate_hardware(
    num_transactions: int,
    tx_profile: TransactionProfile,
    defaults: SizingDefaults,
) -> SizingResult:
    """Calculate CPU / RAM / disk requirements for a given daily transaction volume.

    All calculations assume `num_transactions` represents transactions
    PER DAY. This is a deliberate simplification -- see README for discussion.
    """

    # --- CPU ---
    total_cpu_seconds = (num_transactions * tx_profile.cpu_ms_per_tx) / 1000
    available_seconds = SECONDS_PER_DAY * defaults.cpu_utilization_target
    raw_cpu_cores = total_cpu_seconds / available_seconds
    cpu_cores = max(1, math.ceil(raw_cpu_cores * defaults.safety_margin))

    # --- RAM ---
    # Concurrency is derived via Little's Law: the number of transactions
    # "in flight" at any moment ≈ arrival_rate * processing_time.
    # Can't assume a perfectly even arrival rate throughout the day --
    # `concurrency_factor` acts as a peak-load multiplier on top of the
    # even-distribution baseline (e.g. 1.0 = perfectly even traffic,
    # >1.0 accounts for bursts/peak hours).
    avg_arrivals_per_second = num_transactions / SECONDS_PER_DAY
    processing_time_seconds = tx_profile.cpu_ms_per_tx / 1000
    concurrent_tx = avg_arrivals_per_second * processing_time_seconds * defaults.concurrency_factor
    raw_ram_mb = concurrent_tx * tx_profile.ram_mb_per_tx
    raw_ram_gb = (raw_ram_mb / 1024) * defaults.safety_margin
    ram_gb = _round_up_to_power_of_two(raw_ram_gb)

    # --- DISK ---
    raw_storage_kb = num_transactions * tx_profile.storage_kb_per_tx * defaults.retention_days
    disk_gb = math.ceil((raw_storage_kb / BYTES_PER_GB) * defaults.safety_margin)
    disk_gb = max(1, disk_gb)

    return SizingResult(
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        disk_gb=disk_gb,
        assumptions={
            "transaction_type": tx_profile.name,
            "cpu_utilization_target": defaults.cpu_utilization_target,
            "safety_margin": defaults.safety_margin,
            "concurrency_factor": defaults.concurrency_factor,
            "retention_days": defaults.retention_days,
        },
    )
