import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sizing.models import TransactionProfile, SizingDefaults
from sizing.calculator import calculate_hardware


def make_defaults(**overrides):
    base = dict(
        cpu_utilization_target=0.7,
        safety_margin=1.2,
        retention_days=30,
        concurrency_factor=0.1,
    )
    base.update(overrides)
    return SizingDefaults(**base)


def test_minimum_one_cpu_core():
    profile = TransactionProfile("light", "desc", cpu_ms_per_tx=1, ram_mb_per_tx=1, storage_kb_per_tx=1)
    result = calculate_hardware(10, profile, make_defaults())
    assert result.cpu_cores >= 1


def test_more_transactions_need_more_cpu():
    profile = TransactionProfile("medium", "desc", cpu_ms_per_tx=50, ram_mb_per_tx=100, storage_kb_per_tx=5)
    small = calculate_hardware(10_000, profile, make_defaults())
    large = calculate_hardware(10_000_000, profile, make_defaults())
    assert large.cpu_cores > small.cpu_cores
    assert large.ram_gb >= small.ram_gb
    assert large.disk_gb > small.disk_gb


def test_ram_rounds_to_power_of_two():
    profile = TransactionProfile("medium", "desc", cpu_ms_per_tx=50, ram_mb_per_tx=100, storage_kb_per_tx=5)
    result = calculate_hardware(100_000, profile, make_defaults())
    ram = result.ram_gb
    assert ram & (ram - 1) == 0  # power of two check


def test_safety_margin_increases_result():
    profile = TransactionProfile("medium", "desc", cpu_ms_per_tx=50, ram_mb_per_tx=100, storage_kb_per_tx=5)
    low_margin = calculate_hardware(1_000_000, profile, make_defaults(safety_margin=1.0))
    high_margin = calculate_hardware(1_000_000, profile, make_defaults(safety_margin=2.0))
    assert high_margin.disk_gb >= low_margin.disk_gb
