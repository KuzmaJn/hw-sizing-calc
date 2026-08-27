# Hardware Sizing Calculator

Estimates CPU cores, RAM and disk space needed to run a given daily
volume of transactions.

## How to run

### 1. Get the code

```bash
git clone <your-repo-url>
cd hw-sizing-calculator
```

### 2. Build the Docker image

```bash
docker build -t hw-sizing-calculator .
```

### 3. Run it

```bash
docker run --rm hw-sizing-calculator --transactions 500000 --type medium
```

### 4. Run tests

```bash
docker run --rm --entrypoint python hw-sizing-calculator -m pytest tests/ -v
```

### Example usages

```bash
# Light transactions, high volume
docker run --rm hw-sizing-calculator --transactions 2000000 --type light

# Heavy, compute-intensive transactions
docker run --rm hw-sizing-calculator --transactions 50000 --type heavy

# Using a custom profile config (see "Config files" below)
docker run --rm hw-sizing-calculator --transactions 300000 --type medium --profile config/custom.yaml

# JSON output instead of a table
docker run --rm hw-sizing-calculator --transactions 500000 --type medium --output json
```

### Running locally without Docker

```bash
pip install -r requirements.txt
python cli.py --transactions 500000 --type medium
python -m pytest tests/ -v
```

## Files in this project

- **`cli.py`** — entry point. Parses command-line arguments
  (`--transactions`, `--type`, `--profile`), calls the calculator, and
  prints the result as a table.
- **`sizing/models.py`** — typed data structures (`TransactionProfile`,
  `SizingDefaults`, `SizingResult`) used across the app, so config and
  calculation results have a consistent, checkable shape instead of
  loose dictionaries.
- **`sizing/config_loader.py`** — reads a YAML profile file and turns
  it into the typed objects from `models.py`.
- **`sizing/calculator.py`** — the actual sizing math: CPU, RAM and
  disk estimation. Has no dependency on the CLI or on file I/O, so it
  can be unit-tested on its own and reused elsewhere if needed.
- **`config/generic.yaml`** — default, domain-neutral transaction
  types (`light`, `medium`, `heavy`) with their CPU/RAM/disk cost per
  transaction, plus global defaults (safety margin, utilization
  target, concurrency factor, retention period).
- **`tests/test_calculator.py`** — unit tests covering the calculation
  logic (minimum values, scaling behavior, RAM rounding, safety margin
  effect).
- **`Dockerfile`** — builds a container image that runs the CLI tool;
  also usable to run the test suite (see above).
- **`requirements.txt`** — Python dependencies (`rich`, `PyYAML`,
  `pytest`).

## Config files

Transaction types and their resource costs are **not hardcoded** —
they live in a YAML config file (`config/generic.yaml` by default).
This keeps the calculation logic generic and lets the tool be adapted
to a specific domain or workload without touching any code.

If you need to model transaction types more specifically for your own
use case, you can create a new config file (e.g. `config/custom.yaml`)
following the same structure as `config/generic.yaml`:

```yaml
transaction_types:
  my_transaction_type:
    description: "..."
    cpu_ms_per_tx: <number>
    ram_mb_per_tx: <number>
    storage_kb_per_tx: <number>

defaults:
  cpu_utilization_target: <0-1>
  safety_margin: <e.g. 1.2>
  retention_days: <number>
  concurrency_factor: <number>
```

Then point the CLI at it with `--profile config/custom.yaml`.

## Design decisions

**"Transaction" and "type of transaction" are intentionally abstract.**
The assignment doesn't define them, so the tool treats a "transaction
type" as any named category with a CPU/RAM/disk cost profile, defined
in a config file rather than hardcoded. This keeps the core logic
domain-agnostic and lets new transaction types be added by editing
YAML, not code.

**Inputs are assumed to be daily volumes.** Sizing tools generally need
a time base to convert "N transactions" into "N cores"; a day is a
reasonable default for provisioning decisions. This is a simplification
worth calling out explicitly rather than leaving implicit.

**Concurrency is derived via Little's Law**, not as a flat fraction of
the daily total: `concurrent_transactions ≈ arrival_rate × processing_time`,
scaled by a configurable peak-load multiplier. An earlier version used
a flat percentage of daily volume, which produced unrealistic results
at scale (e.g. thousands of GB of RAM for a moderate transaction
count) — switching to an arrival-rate-based model fixed this.

**Safety margins and utilization targets are parameters, not constants.**
Real sizing never plans for 100% utilization; how much headroom to
leave is a business decision, so it lives in config, not code.

**What was rejected:**

- A web UI — out of scope for what's being evaluated; a CLI table is a
  complete answer per the assignment.
- Persisting results to a database — this is a one-shot calculation,
  not a service with state.
- A "smart"/ML-based estimator — a transparent, explainable linear
  model is more appropriate for a sizing tool people need to trust and
  audit.

## Project structure

```
cli.py                    # CLI entry point (argument parsing, output)
sizing/
  models.py                # typed data structures
  config_loader.py          # YAML -> typed config
  calculator.py             # core sizing math (framework-independent, unit-tested)
config/
  generic.yaml               # domain-neutral transaction profiles
tests/
  test_calculator.py          # unit tests for the calculation logic
Dockerfile
requirements.txt
```
