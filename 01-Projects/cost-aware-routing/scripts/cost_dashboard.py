#!/usr/bin/env python3
"""
cost_dashboard.py — Generate an HTML dashboard from the cost audit log.

Reads the persistent cost-audit-log.jsonl and produces a standalone HTML
file with charts (using Chart.js from CDN), tables, and summary stats.

Usage:
    python3 cost_dashboard.py                    # Generate and open
    python3 cost_dashboard.py --output report.html
    python3 cost_dashboard.py --no-open          # Generate without opening
    python3 cost_dashboard.py --days 7            # Last N days only
"""

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
COST_LOG_PATH = PROJECT_ROOT / "data" / "cost-audit-log.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "data"
DEFAULT_OUTPUT = OUTPUT_DIR / "cost-dashboard.html"


def load_entries(log_path: Path, days: int = None) -> list:
    """Load cost entries from audit log."""
    entries = []
    cutoff = None
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    if not log_path.exists():
        return entries

    with open(log_path) as f:
        for line in f:
            try:
                d = json.loads(line)
                if d.get("event_type") == "session_summary":
                    continue  # Skip summaries for chart data
                if cutoff and d.get("timestamp", "") < cutoff:
                    continue
                entries.append(d)
            except json.JSONDecodeError:
                continue

    return entries


def aggregate(entries: list) -> dict:
    """Aggregate entries by model, date, session, venue."""
    by_model = defaultdict(lambda: {"turns": 0, "cost": 0.0, "input_tokens": 0, "output_tokens": 0})
    by_date = defaultdict(lambda: {"cost": 0.0, "turns": 0, "local": 0.0, "cloud": 0.0})
    by_session = defaultdict(lambda: {"cost": 0.0, "turns": 0, "models": set()})
    by_venue = {"local": 0.0, "cloud": 0.0}
    by_hour = defaultdict(lambda: {"cost": 0.0, "turns": 0})

    for e in entries:
        model = e.get("model", "unknown")
        cost = e.get("cost_usd", 0)
        ts = e.get("timestamp", "")
        venue = "cloud" if (":cloud" in model or "cloud" in model.lower()) else "local"

        # By model
        by_model[model]["turns"] += 1
        by_model[model]["cost"] += cost
        by_model[model]["input_tokens"] += e.get("input_tokens", 0)
        by_model[model]["output_tokens"] += e.get("output_tokens", 0)

        # By date
        if ts:
            date_key = ts[:10]
        else:
            date_key = "unknown"
        by_date[date_key]["cost"] += cost
        by_date[date_key]["turns"] += 1
        by_date[date_key][venue] += cost

        # By session
        sid = e.get("session_id", "unknown")[:12]
        by_session[sid]["cost"] += cost
        by_session[sid]["turns"] += 1
        by_session[sid]["models"].add(model)

        # By venue
        by_venue[venue] += cost

        # By hour of day
        if ts:
            try:
                hour = datetime.fromisoformat(ts.replace("Z", "+00:00")).hour
                by_hour[hour]["cost"] += cost
                by_hour[hour]["turns"] += 1
            except:
                pass

    # Convert sets to sorted lists for JSON serialization
    for sid in by_session:
        by_session[sid]["models"] = sorted(by_session[sid]["models"])

    return {
        "by_model": dict(by_model),
        "by_date": dict(by_date),
        "by_session": dict(by_session),
        "by_venue": by_venue,
        "by_hour": dict(by_hour),
        "total_cost": sum(e.get("cost_usd", 0) for e in entries),
        "total_turns": len(entries),
        "total_input_tokens": sum(e.get("input_tokens", 0) for e in entries),
        "total_output_tokens": sum(e.get("output_tokens", 0) for e in entries),
    }


def generate_html(agg: dict, entries: list, output_path: Path) -> str:
    """Generate standalone HTML dashboard."""
    # Sort models by cost descending
    models_sorted = sorted(agg["by_model"].items(), key=lambda x: -x[1]["cost"])
    dates_sorted = sorted(agg["by_date"].items())
    sessions_sorted = sorted(agg["by_session"].items(), key=lambda x: -x[1]["cost"])

    # Chart data
    model_names = [m[0] for m in models_sorted]
    model_costs = [round(m[1]["cost"], 4) for m in models_sorted]
    model_turns = [m[1]["turns"] for m in models_sorted]

    date_labels = [d[0] for d in dates_sorted]
    date_costs = [round(d[1]["cost"], 4) for d in dates_sorted]
    date_local = [round(d[1].get("local", 0), 4) for d in dates_sorted]
    date_cloud = [round(d[1].get("cloud", 0), 4) for d in dates_sorted]

    hour_labels = [str(h) for h in sorted(agg["by_hour"].keys())]
    hour_costs = [round(agg["by_hour"][h]["cost"], 4) for h in sorted(agg["by_hour"].keys())]

    # Top 20 most expensive turns
    top_turns = sorted(entries, key=lambda e: -e.get("cost_usd", 0))[:20]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cost-Aware Routing — Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #242838;
    --text: #e1e4ed;
    --text2: #8b8fa3;
    --accent: #6366f1;
    --accent2: #22d3ee;
    --local: #34d399;
    --cloud: #f59e0b;
    --danger: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 24px;
    max-width: 1400px;
    margin: 0 auto;
  }}
  h1 {{ font-size: 1.5rem; margin-bottom: 8px; }}
  h2 {{ font-size: 1.1rem; color: var(--text2); margin: 24px 0 12px; text-transform: uppercase; letter-spacing: 1px; }}
  .header {{ margin-bottom: 24px; }}
  .header .subtitle {{ color: var(--text2); font-size: 0.85rem; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .card {{
    background: var(--surface);
    border: 1px solid var(--surface2);
    border-radius: 12px;
    padding: 20px;
  }}
  .card .label {{ color: var(--text2); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }}
  .card .value {{ font-size: 1.75rem; font-weight: 700; margin-top: 4px; }}
  .card .sub {{ color: var(--text2); font-size: 0.8rem; margin-top: 4px; }}
  .card.cost .value {{ color: var(--accent2); }}
  .card.local .value {{ color: var(--local); }}
  .card.cloud .value {{ color: var(--cloud); }}
  .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
  .chart-card {{
    background: var(--surface);
    border: 1px solid var(--surface2);
    border-radius: 12px;
    padding: 20px;
  }}
  .chart-card.full {{ grid-column: 1 / -1; }}
  canvas {{ max-height: 300px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
  }}
  th {{
    text-align: left;
    padding: 8px 12px;
    color: var(--text2);
    border-bottom: 1px solid var(--surface2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.7rem;
  }}
  td {{ padding: 8px 12px; border-bottom: 1px solid var(--surface2); }}
  tr:hover {{ background: var(--surface2); }}
  .tag {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
  }}
  .tag.local {{ background: rgba(52,211,153,0.15); color: var(--local); }}
  .tag.cloud {{ background: rgba(245,158,11,0.15); color: var(--cloud); }}
  .venue-bar {{ display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 8px; }}
  .venue-bar .local {{ background: var(--local); }}
  .venue-bar .cloud {{ background: var(--cloud); }}
  @media (max-width: 768px) {{
    .charts {{ grid-template-columns: 1fr; }}
    .cards {{ grid-template-columns: 1fr 1fr; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>💰 Cost-Aware Routing Dashboard</h1>
  <div class="subtitle">TI-018 • Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} • {len(entries)} turns logged</div>
</div>

<div class="cards">
  <div class="card cost">
    <div class="label">Total Cost</div>
    <div class="value">${agg['total_cost']:.4f}</div>
    <div class="sub">{agg['total_turns']} turns</div>
  </div>
  <div class="card local">
    <div class="label">Local Cost</div>
    <div class="value">${agg['by_venue']['local']:.4f}</div>
    <div class="sub">{agg['by_venue']['local']/max(agg['total_cost'],0.01)*100:.0f}% of total</div>
  </div>
  <div class="card cloud">
    <div class="label">Cloud Cost</div>
    <div class="value">${agg['by_venue']['cloud']:.4f}</div>
    <div class="sub">{agg['by_venue']['cloud']/max(agg['total_cost'],0.01)*100:.0f}% of total</div>
  </div>
  <div class="card">
    <div class="label">Total Tokens</div>
    <div class="value">{(agg['total_input_tokens'] + agg['total_output_tokens'])/1_000_000:.1f}M</div>
    <div class="sub">{agg['total_input_tokens']/1_000_000:.1f}M in + {agg['total_output_tokens']/1_000_000:.1f}M out</div>
  </div>
</div>

<div class="venue-bar">
  <div class="local" style="width: {agg['by_venue']['local']/max(agg['total_cost'],0.01)*100}%"></div>
  <div class="cloud" style="width: {agg['by_venue']['cloud']/max(agg['total_cost'],0.01)*100}%"></div>
</div>

<h2>Cost Over Time</h2>
<div class="charts">
  <div class="chart-card full">
    <canvas id="costOverTime"></canvas>
  </div>
</div>

<h2>By Model</h2>
<div class="charts">
  <div class="chart-card">
    <canvas id="costByModel"></canvas>
  </div>
  <div class="chart-card">
    <canvas id="turnsByModel"></canvas>
  </div>
</div>

<h2>Usage Patterns</h2>
<div class="charts">
  <div class="chart-card">
    <canvas id="costByHour"></canvas>
  </div>
  <div class="chart-card">
    <canvas id="venueOverTime"></canvas>
  </div>
</div>

<h2>Models — Detail</h2>
<div class="chart-card" style="margin-bottom: 24px;">
  <table>
    <thead>
      <tr>
        <th>Model</th>
        <th>Venue</th>
        <th>Turns</th>
        <th>Input Tokens</th>
        <th>Output Tokens</th>
        <th>Cost</th>
        <th>Cost/Turn</th>
      </tr>
    </thead>
    <tbody>
      {"".join(f'''
      <tr>
        <td>{m}</td>
        <td><span class="tag {"cloud" if ":cloud" in m or "cloud" in m.lower() else "local"}">{"cloud" if ":cloud" in m or "cloud" in m.lower() else "local"}</span></td>
        <td>{d["turns"]}</td>
        <td>{d["input_tokens"]:,}</td>
        <td>{d["output_tokens"]:,}</td>
        <td>${d["cost"]:.4f}</td>
        <td>${d["cost"]/max(d["turns"],1):.4f}</td>
      </tr>''' for m, d in models_sorted)}
    </tbody>
  </table>
</div>

<h2>Sessions — Top 10 by Cost</h2>
<div class="chart-card" style="margin-bottom: 24px;">
  <table>
    <thead>
      <tr><th>Session</th><th>Turns</th><th>Models</th><th>Cost</th></tr>
    </thead>
    <tbody>
      {"".join(f'''
      <tr>
        <td>{sid}...</td>
        <td>{d["turns"]}</td>
        <td>{", ".join(d["models"])}</td>
        <td>${d["cost"]:.4f}</td>
      </tr>''' for sid, d in sessions_sorted[:10])}
    </tbody>
  </table>
</div>

<h2>Top 20 Most Expensive Turns</h2>
<div class="chart-card" style="margin-bottom: 24px;">
  <table>
    <thead>
      <tr><th>#</th><th>Timestamp</th><th>Model</th><th>Input</th><th>Output</th><th>Cost</th></tr>
    </thead>
    <tbody>
      {"".join(f'''
      <tr>
        <td>{i+1}</td>
        <td>{e.get("timestamp","")[:16]}</td>
        <td>{e.get("model","?")}</td>
        <td>{e.get("input_tokens",0):,}</td>
        <td>{e.get("output_tokens",0):,}</td>
        <td>${e.get("cost_usd",0):.4f}</td>
      </tr>''' for i, e in enumerate(top_turns))}
    </tbody>
  </table>
</div>

<script>
// Cost Over Time
new Chart(document.getElementById('costOverTime'), {{
  type: 'line',
  data: {{
    labels: {json.dumps(date_labels)},
    datasets: [{{
      label: 'Daily Cost ($)',
      data: {json.dumps(date_costs)},
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99,102,241,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ title: {{ display: true, text: 'Cost ($)' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      x: {{ grid: {{ display: false }} }}
    }}
  }}
}});

// Cost by Model
new Chart(document.getElementById('costByModel'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(model_names)},
    datasets: [{{
      label: 'Cost ($)',
      data: {json.dumps(model_costs)},
      backgroundColor: model_names.map(m => m.includes(':cloud') || m.toLowerCase().includes('cloud') ? 'rgba(245,158,11,0.7)' : 'rgba(52,211,153,0.7)'),
      borderRadius: 6,
    }}]
  }},
  options: {{
    responsive: true,
    indexAxis: 'y',
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ title: {{ display: true, text: 'Cost ($)' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});

// Turns by Model
new Chart(document.getElementById('turnsByModel'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(model_names)},
    datasets: [{{
      label: 'Turns',
      data: {json.dumps(model_turns)},
      backgroundColor: 'rgba(99,102,241,0.6)',
      borderRadius: 6,
    }}]
  }},
  options: {{
    responsive: true,
    indexAxis: 'y',
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});

// Cost by Hour
new Chart(document.getElementById('costByHour'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(hour_labels)},
    datasets: [{{
      label: 'Cost ($)',
      data: {json.dumps(hour_costs)},
      backgroundColor: 'rgba(34,211,238,0.6)',
      borderRadius: 6,
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ title: {{ display: true, text: 'Cost ($)' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      x: {{ title: {{ display: true, text: 'Hour of Day' }}, grid: {{ display: false }} }}
    }}
  }}
}});

// Venue Over Time (stacked)
new Chart(document.getElementById('venueOverTime'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(date_labels)},
    datasets: [
      {{
        label: 'Local',
        data: {json.dumps(date_local)},
        backgroundColor: 'rgba(52,211,153,0.7)',
        borderRadius: 6,
      }},
      {{
        label: 'Cloud',
        data: {json.dumps(date_cloud)},
        backgroundColor: 'rgba(245,158,11,0.7)',
        borderRadius: 6,
      }}
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      y: {{ stacked: true, title: {{ display: true, text: 'Cost ($)' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      x: {{ stacked: true, grid: {{ display: false }} }}
    }}
  }}
}});
</script>

</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate cost dashboard HTML")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output HTML file path")
    parser.add_argument("--no-open", action="store_true", help="Don't open in browser")
    parser.add_argument("--days", type=int, default=None, help="Last N days only")
    args = parser.parse_args()

    entries = load_entries(COST_LOG_PATH, args.days)
    if not entries:
        print(f"No cost entries found in {COST_LOG_PATH}", file=sys.stderr)
        sys.exit(1)

    agg = aggregate(entries)
    html = generate_html(agg, entries, Path(args.output))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(html)

    print(f"Dashboard generated: {args.output}")
    print(f"  {len(entries)} entries, ${agg['total_cost']:.4f} total cost")
    print(f"  Models: {', '.join(m for m, _ in sorted(agg['by_model'].items(), key=lambda x: -x[1]['cost']))}")

    if not args.no_open:
        subprocess.run(["open", args.output], check=False)


if __name__ == "__main__":
    main()