<h1 align="center">(Unofficial) Scalable CLI Python API</h1>

<p align="center"><strong>The Pythonic wrapper for the Scalable Broker CLI.</strong></p>

<p align="center">Built for developers that need commands, structured data models, and a Python API for the Scalable Capital Broker.</p>

<br />

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#common-operations">Common operations</a> ·
  <a href="#cli-management">CLI Management</a>
</p>

<br />

`sc-cli-py` is a high-level Python wrapper around the [Scalable CLI](https://github.com/ScalableCapital/scalable-cli). It provides a state-driven, object-oriented interface to interact with your Scalable Broker account programmatically, replacing raw JSON parsing with Pydantic models.

## Why use `sc-cli-py`

- **Type Safety**: Fully typed Pydantic models for holdings, transactions, overview, and search results.
- **Automated CLI Installation**: Handles downloading, installing, and updating the underlying CLI binary automatically.

## Affiliation

This project is **not** affiliated with Scalable Capital. It is a personal project. **If you are Scalable Capital and want me to take this project down, please open an Issue and I will comply immediately.** That said, I'd appreciate it if the community is allowed to build upon the CLI as it is common practice in the tech world.

The wrapper just uses the official [Scalable CLI](https://github.com/ScalableCapital/scalable-cli). For more information on the underlying capabilities, refer to the original documentation or the `capabilities` command.

> [!CAUTION]
> This API has full power over your Scalable Capital account.
>   - Do **NOT** rely on this code for anything but your personal projects.
>   - Do **NOT** use this code unless you understand every line yourself. The code may contain bugs or unexpected behavior.
>   - **YOU** are responsible for all of your actions. (Algorithmic) Trading is risky and I discourage everyone to use this API for anything beyond a hobby project.

## Install (not available on PyPi yet)

```bash
pip install sc-cli-py
```

## Quick start

The library uses a stateful approach. You first initialize the API, then log in to get an active `Broker` session.

```python
from sc_api import ScalableAPI

# 1. Initialize API (handles CLI binary automatically)
api = ScalableAPI()

# 2. Login (Smart flow: checks session, then goes interactive if needed)
broker = api.login()
print(f"Logged in as: {broker.user.first_name} {broker.user.last_name}")

# 3. Access Broker features directly
holdings = broker.get_holdings()
for item in holdings:
    print(f"{item.name}: {item.quantity} units")
```

> [!TIP]
> Authentication will only work if your Scalable account is approved for CLI use. Read the official [Scalable CLI](https://github.com/ScalableCapital/scalable-cli) docs to learn more.

## Common operations

### Portfolio Overview

Get a high-level summary of your portfolio performance and valuation.

```python
overview = broker.get_overview()
print(f"Total Value: {overview.total:,.2f} EUR")
print(f"Securities:  {overview.securities:,.2f} EUR")
```

### Trading

Trading is an intentional two-step flow to ensure precision and allow for review.

```python
# Phase 1: Preview (No confirm_id)
# Use isin, and amount (for buy) or shares (for sell)
preview = broker.trade_buy(isin="ISIN_HERE", amount=100)
print(f"Status: {preview.status}")

# Phase 2: Confirm (Using confirmation_id from preview)
# if preview.confirmation_id:
#     result = broker.trade_buy(
#         isin="ISIN_HERE", 
#         amount=100, 
#         confirm_id=preview.confirmation_id
#     )
#     print(f"Order Placed! ID: {result.order_id}")
```

> [!CAUTION]
> It is highly advised that you treat this confirmation workflow as an actual human-in-the-loop approach. Spreads, fees, and other costs do apply and may add unexpectedly to the final cost of the trade. Ensure that all of information is clearly displayed to the account holder before confirmation is given.

### Searching Instruments

```python
results = broker.search("Apple")
for security in results:
    print(f"{security.name} ({security.isin}) -> {security.quote_mid_price} {security.quote_currency}")
```

## CLI Management

The library automatically manages the underlying `sc` CLI binary in a user-specific data directory. If you need manual control:

```python
from sc_api import CLIManager

mgr = CLIManager()
if not mgr.is_installed():
    mgr.download_and_install()

print(f"CLI Path: {mgr.get_bin_path()}")
print(f"CLI Version: {mgr.version}")
```

## Configuration

`sc-cli-py` respects the same configuration as the Scalable CLI. You can configure backends (keyring, secure enclave) via `config.toml`.

See [CLI Documentation](CLI_README.md#configuration) for details on setting up secure storage for sessions and keys.
