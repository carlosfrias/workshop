#!/usr/bin/env python3
"""
invoice_generator.py — Generate Markdown invoices from customer usage data.

Reads aggregated customer usage (JSONL) and generates Markdown invoices.
Invoices are saved to the vault for authoritative record-keeping.

Usage:
    # Generate invoices for all customers (current month)
    python3 invoice_generator.py

    # Generate for specific month
    python3 invoice_generator.py --month 2026-05

    # Generate for specific customer
    python3 invoice_generator.py --customer customer-001

    # Preview invoice (stdout)
    python3 invoice_generator.py --customer customer-001 --preview
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
USAGE_INPUT_PATH = DATA_DIR / "customer-usage.jsonl"

# Vault paths
VAULT_ROOT = Path.home() / "Cloud" / "carlos-desktop" / "personal-vault"
VAULT_INVOICES_DIR = VAULT_ROOT / "01-Projects" / "cost-aware-routing" / "invoices"


def load_usage_data(usage_path: Path = None, month: str = None) -> list:
    """Load customer usage data from JSONL."""
    if usage_path is None:
        if month:
            usage_path = DATA_DIR / f"customer-usage-{month}.jsonl"
        else:
            usage_path = USAGE_INPUT_PATH
    
    if not usage_path.exists():
        print(f"Error: Usage data not found at {usage_path}")
        print("Run usage_tracker.py first to generate usage data.")
        sys.exit(1)
    
    customers = []
    with open(usage_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    customers.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return customers


def get_billing_tiers() -> dict:
    """Load billing tier definitions."""
    config_path = PROJECT_ROOT / "config" / "billing_tiers.json"
    if not config_path.exists():
        # Return default tiers if config not found
        return {
            "Local Basic": {"model": "qwen3.5:4b", "price_per_1k": 0.0050},
            "Local Standard": {"model": "qwen3:8b", "price_per_1k": 0.0060},
            "Local Premium": {"model": "gemma4:e4b", "price_per_1k": 0.0050},
            "Cloud Standard": {"model": "gemma4:31b-cloud", "price_per_1k": 0.0150},
            "Cloud Premium": {"model": "kimi-k2.6:cloud", "price_per_1k": 0.0500}
        }
    
    with open(config_path) as f:
        data = json.load(f)
    
    # Convert list format to dict for easy lookup
    tiers = {}
    for tier in data.get("tiers", []):
        tiers[tier["name"]] = {
            "model": tier.get("model"),
            "price_per_1k": tier.get("price_per_1k", 0.0050)
        }
    return tiers


def generate_invoice(customer: dict, billing_tiers: dict) -> str:
    """Generate Markdown invoice content."""
    customer_id = customer.get("customer_id", "unknown")
    total_cost = customer.get("total_cost", 0)
    total_input = customer.get("total_input_tokens", 0)
    total_output = customer.get("total_output_tokens", 0)
    total_tasks = customer.get("total_tasks", 0)
    models_used = customer.get("models_used", {})
    first_use = customer.get("first_use", "")
    last_use = customer.get("last_use", "")
    generated_at = customer.get("generated_at", datetime.now().isoformat())
    
    # Parse dates for display
    try:
        first_date = datetime.fromisoformat(first_use).strftime("%Y-%m-%d %H:%M")
        last_date = datetime.fromisoformat(last_use).strftime("%Y-%m-%d %H:%M")
    except:
        first_date = first_use
        last_date = last_use
    
    invoice_month = last_use[:7] if last_use else datetime.now().strftime("%Y-%m")
    invoice_date = datetime.now().strftime("%Y-%m-%d")
    invoice_number = f"INV-{invoice_month.replace('-', '')}-{customer_id}"
    
    # Build usage table by model
    usage_rows = []
    for model, count in sorted(models_used.items()):
        # Find tier for this model
        tier_name = "Custom"
        price_per_1k = 0.0050  # default
        for t_name, t_data in billing_tiers.items():
            if t_data.get("model") == model:
                tier_name = t_name
                price_per_1k = t_data.get("price_per_1k", 0.0050)
                break
        
        usage_rows.append({
            "model": model,
            "tier": tier_name,
            "requests": count,
            "price_per_1k": price_per_1k
        })
    
    # Generate Markdown
    md = f"""---
type: invoice
domain: cost-aware-routing
customer: {customer_id}
invoice_number: {invoice_number}
invoice_date: {invoice_date}
service_period_start: {first_use[:10] if first_use else ""}
service_period_end: {last_use[:10] if last_use else ""}
total_amount: {total_cost:.4f}
status: pending
---

# Invoice

**Invoice Number:** {invoice_number}  
**Date:** {invoice_date}  
**Customer:** {customer_id}

---

## Service Period

| Start Date | End Date |
|------------|----------|
| {first_date} | {last_date} |

---

## Usage Summary

| Metric | Value |
|--------|-------|
| Total Requests | {total_tasks:,} |
| Input Tokens | {total_input:,} |
| Output Tokens | {total_output:,} |
| **Total Tokens** | **{total_input + total_output:,}** |

---

## Usage by Model

| Model | Tier | Requests | Price/1K | Subtotal |
|-------|------|----------|----------|----------|
"""
    
    # Add usage rows (we don't have per-model token counts, so estimate)
    total_requests = sum(r["requests"] for r in usage_rows) or 1
    avg_tokens = (total_input + total_output) / total_requests if total_requests else 0
    
    for row in usage_rows:
        subtotal = (avg_tokens * row["requests"] / 1000) * row["price_per_1k"]
        md += f"| {row['model']} | {row['tier']} | {row['requests']:,} | ${row['price_per_1k']:.4f} | ${subtotal:.4f} |\n"
    
    md += f"""
---

## Billing Summary

| Description | Amount |
|-------------|--------|
| Usage charges | ${total_cost:.4f} |
| **Total Due** | **${total_cost:.4f}** |

---

## Payment Terms

Payment due within 30 days of invoice date.

---

*Generated: {generated_at}*  
*Invoice stored in: `01-Projects/cost-aware-routing/invoices/{invoice_month}/{invoice_number}.md`*
"""
    
    return md


def save_invoice(invoice_md: str, customer_id: str, month: str = None) -> Path:
    """Save invoice to vault."""
    # Determine invoice month
    if not month:
        month = datetime.now().strftime("%Y-%m")
    
    # Create month directory
    month_dir = VAULT_INVOICES_DIR / month
    month_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    invoice_number = f"INV-{month.replace('-', '')}-{customer_id}"
    invoice_path = month_dir / f"{invoice_number}.md"
    
    # Write invoice
    with open(invoice_path, 'w') as f:
        f.write(invoice_md)
    
    return invoice_path


def main():
    parser = argparse.ArgumentParser(description="Generate Markdown invoices from usage data")
    parser.add_argument("--month", help="Generate for specific month (YYYY-MM)")
    parser.add_argument("--customer", help="Generate for specific customer ID")
    parser.add_argument("--preview", action="store_true", help="Preview invoice to stdout")
    args = parser.parse_args()
    
    # Load usage data
    print(f"Loading usage data...")
    customers = load_usage_data(month=args.month)
    print(f"Found {len(customers):,} customer(s)")
    
    # Load billing tiers
    billing_tiers = get_billing_tiers()
    
    # Filter by customer if specified
    if args.customer:
        customers = [c for c in customers if c.get("customer_id") == args.customer]
        if not customers:
            print(f"No usage data found for customer: {args.customer}")
            sys.exit(1)
    
    # Generate invoices
    for customer in customers:
        customer_id = customer.get("customer_id", "unknown")
        print(f"\nGenerating invoice for {customer_id}...")
        
        invoice_md = generate_invoice(customer, billing_tiers)
        
        if args.preview:
            print("\n" + "=" * 60)
            print(invoice_md)
            print("=" * 60)
        else:
            invoice_path = save_invoice(invoice_md, customer_id, args.month)
            print(f"  Saved: {invoice_path}")
    
    print(f"\nDone. Generated {len(customers)} invoice(s).")


if __name__ == "__main__":
    main()
