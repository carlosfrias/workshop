#!/usr/bin/env python3
"""
billing_dashboard.py — Generate interactive HTML dashboard for billing data.

Creates a self-contained HTML file with:
- Customer usage summary
- Invoice status
- Time-cost analysis
- Interactive charts (Chart.js)

Usage:
    python3 billing_dashboard.py
    
Output:
    analysis/billing-dashboard.html
"""

import json
from datetime import datetime
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
COST_LOG_PATH = DATA_DIR / "cost-audit-log.jsonl"
USAGE_PATH = DATA_DIR / "customer-usage.jsonl"


def load_usage_data() -> list:
    """Load customer usage data."""
    if not USAGE_PATH.exists():
        return []
    
    customers = []
    with open(USAGE_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    customers.append(json.loads(line))
                except:
                    continue
    return customers


def load_cost_log() -> list:
    """Load cost audit log."""
    if not COST_LOG_PATH.exists():
        return []
    
    entries = []
    with open(COST_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except:
                    continue
    return entries


def generate_dashboard_html(usage_data: list, cost_log: list) -> str:
    """Generate complete HTML dashboard."""
    
    # Calculate summary metrics
    total_customers = len(usage_data)
    total_cost = sum(c.get("total_cost", 0) for c in usage_data)
    total_tokens = sum(c.get("total_input_tokens", 0) + c.get("total_output_tokens", 0) for c in usage_data)
    total_tasks = sum(c.get("total_tasks", 0) for c in usage_data)
    
    # Top customers by cost
    top_customers = sorted(usage_data, key=lambda x: x.get("total_cost", 0), reverse=True)[:10]
    
    # Model usage breakdown
    model_usage = {}
    for customer in usage_data:
        for model, count in customer.get("models_used", {}).items():
            if model not in model_usage:
                model_usage[model] = 0
            model_usage[model] += count
    
    # Time series data (by date)
    daily_costs = {}
    for entry in cost_log:
        date = entry.get("timestamp", "")[:10]
        if date:
            daily_costs[date] = daily_costs.get(date, 0) + entry.get("cost_usd", 0)
    
    daily_dates = sorted(daily_costs.keys())
    daily_values = [daily_costs[d] for d in daily_dates]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cost-Aware Routing — Billing Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #2563eb;
            --secondary: #64748b;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 2rem;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--secondary);
            font-size: 1rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .metric-sub {{
            font-size: 0.875rem;
            color: var(--secondary);
            margin-top: 0.25rem;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .chart-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        .table-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            text-align: left;
            padding: 0.75rem;
            background: var(--bg);
            font-weight: 600;
            border-bottom: 2px solid var(--bg);
        }}
        
        td {{
            padding: 0.75rem;
            border-bottom: 1px solid var(--bg);
        }}
        
        tr:hover {{
            background: var(--bg);
        }}
        
        .generated {{
            text-align: center;
            color: var(--secondary);
            font-size: 0.875rem;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Billing Dashboard</h1>
            <div class="subtitle">Cost-Aware Routing Project</div>
        </header>
        
        <!-- Summary Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">${total_cost:,.2f}</div>
                <div class="metric-sub">All customers</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Customers</div>
                <div class="metric-value">{total_customers:,}</div>
                <div class="metric-sub">Active accounts</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tasks</div>
                <div class="metric-value">{total_tasks:,}</div>
                <div class="metric-sub">Requests processed</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tokens</div>
                <div class="metric-value">{total_tokens/1_000_000:.2f}M</div>
                <div class="metric-sub">Input + output</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">Daily Cost Trend</div>
                <canvas id="dailyChart"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-title">Model Usage Distribution</div>
                <canvas id="modelChart"></canvas>
            </div>
        </div>
        
        <!-- Top Customers Table -->
        <div class="table-card">
            <h2 class="chart-title">Top 10 Customers by Cost</h2>
            <table>
                <thead>
                    <tr>
                        <th>Customer ID</th>
                        <th>Tasks</th>
                        <th>Tokens</th>
                        <th>Total Cost</th>
                        <th>Last Activity</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for customer in top_customers:
        cust_id = customer.get("customer_id", "unknown")[:20]
        tasks = customer.get("total_tasks", 0)
        tokens = customer.get("total_input_tokens", 0) + customer.get("total_output_tokens", 0)
        cost = customer.get("total_cost", 0)
        last_use = customer.get("last_use", "")[:10]
        
        html += f"""                    <tr>
                        <td><code>{cust_id}</code></td>
                        <td>{tasks:,}</td>
                        <td>{tokens/1_000_000:.2f}M</td>
                        <td>${cost:,.2f}</td>
                        <td>{last_use}</td>
                    </tr>
"""
    
    html += f"""                </tbody>
            </table>
        </div>
        
        <div class="generated">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Daily Cost Chart
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        new Chart(dailyCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(daily_dates[-30:])},
                datasets: [{{
                    label: 'Daily Cost (USD)',
                    data: {json.dumps(daily_values[-30:])},
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Model Usage Chart
        const modelCtx = document.getElementById('modelChart').getContext('2d');
        new Chart(modelCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(list(model_usage.keys())[:10])},
                datasets: [{{
                    data: {json.dumps(list(model_usage.values())[:10])},
                    backgroundColor: [
                        '#2563eb',
                        '#3b82f6',
                        '#60a5fa',
                        '#93c5fd',
                        '#dbeafe',
                        '#1e40af',
                        '#1e3a8a',
                        '#172554',
                        '#64748b',
                        '#94a3b8'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'right'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    return html


def main():
    print("Loading usage data...")
    usage_data = load_usage_data()
    print(f"Loaded {len(usage_data)} customers")
    
    print("Loading cost log...")
    cost_log = load_cost_log()
    print(f"Loaded {len(cost_log)} entries")
    
    print("Generating dashboard...")
    html = generate_dashboard_html(usage_data, cost_log)
    
    # Save dashboard
    dashboard_path = ANALYSIS_DIR / "billing-dashboard.html"
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(dashboard_path, 'w') as f:
        f.write(html)
    
    print(f"✓ Dashboard saved to: {dashboard_path}")
    print(f"  Open in browser to view")


if __name__ == "__main__":
    main()
