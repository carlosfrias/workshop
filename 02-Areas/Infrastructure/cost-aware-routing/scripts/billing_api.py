#!/usr/bin/env python3
"""
billing_api.py — REST API endpoints for billing data.

Provides JSON API for:
- Customer usage data
- Invoice listings
- Cost analytics
- Time-cost analysis

Usage:
    python3 billing_api.py
    
Endpoints:
    GET /api/customers           - List all customers
    GET /api/customers/{id}      - Get customer details
    GET /api/invoices            - List invoices
    GET /api/invoices/{month}    - Get invoices for month
    GET /api/analytics/summary   - Cost analytics summary
    GET /api/analytics/time-cost - Time-cost analysis
"""

import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
VAULT_ROOT = Path.home() / "Cloud" / "carlos-desktop" / "personal-vault"
VAULT_INVOICES_DIR = VAULT_ROOT / "01-Projects" / "cost-aware-routing" / "invoices"

COST_LOG_PATH = DATA_DIR / "cost-audit-log.jsonl"
USAGE_PATH = DATA_DIR / "customer-usage.jsonl"


class BillingAPIHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for billing API."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Route requests
        if path == '/api/customers':
            self.send_json_response(self.get_customers())
        elif path.startswith('/api/customers/'):
            customer_id = path.split('/')[-1]
            self.send_json_response(self.get_customer(customer_id))
        elif path == '/api/invoices':
            self.send_json_response(self.get_invoices())
        elif path.startswith('/api/invoices/'):
            month = path.split('/')[-1]
            self.send_json_response(self.get_invoices_for_month(month))
        elif path == '/api/analytics/summary':
            self.send_json_response(self.get_analytics_summary())
        elif path == '/api/analytics/time-cost':
            self.send_json_response(self.get_time_cost_analysis())
        elif path == '/api/health':
            self.send_json_response({"status": "healthy", "timestamp": datetime.now().isoformat()})
        else:
            self.send_error(404, "Not Found")
    
    def send_json_response(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def get_customers(self) -> dict:
        """Get list of all customers."""
        if not USAGE_PATH.exists():
            return {"error": "No usage data available"}
        
        customers = []
        with open(USAGE_PATH) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        customers.append(json.loads(line))
                    except:
                        continue
        
        return {
            "count": len(customers),
            "customers": customers
        }
    
    def get_customer(self, customer_id: str) -> dict:
        """Get details for a specific customer."""
        if not USAGE_PATH.exists():
            return {"error": "No usage data available"}
        
        with open(USAGE_PATH) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        customer = json.loads(line)
                        if customer.get("customer_id") == customer_id:
                            return customer
                    except:
                        continue
        
        return {"error": f"Customer {customer_id} not found"}
    
    def get_invoices(self) -> dict:
        """Get list of all invoices."""
        if not VAULT_INVOICES_DIR.exists():
            return {"error": "No invoices found"}
        
        invoices = []
        for month_dir in sorted(VAULT_INVOICES_DIR.iterdir()):
            if month_dir.is_dir():
                month = month_dir.name
                for invoice_file in month_dir.glob("*.md"):
                    invoices.append({
                        "month": month,
                        "filename": invoice_file.name,
                        "path": str(invoice_file.relative_to(VAULT_ROOT))
                    })
        
        return {
            "count": len(invoices),
            "invoices": invoices
        }
    
    def get_invoices_for_month(self, month: str) -> dict:
        """Get invoices for a specific month."""
        month_dir = VAULT_INVOICES_DIR / month
        
        if not month_dir.exists():
            return {"error": f"No invoices found for {month}"}
        
        invoices = []
        for invoice_file in month_dir.glob("*.md"):
            # Parse frontmatter
            with open(invoice_file) as f:
                content = f.read()
            
            # Extract customer and amount from filename
            filename = invoice_file.name
            customer = filename.replace(f"INV-{month.replace('-', '')}-", "").replace(".md", "")
            
            invoices.append({
                "filename": filename,
                "customer": customer,
                "path": str(invoice_file.relative_to(VAULT_ROOT))
            })
        
        return {
            "month": month,
            "count": len(invoices),
            "invoices": invoices
        }
    
    def get_analytics_summary(self) -> dict:
        """Get cost analytics summary."""
        if not COST_LOG_PATH.exists():
            return {"error": "No cost log available"}
        
        entries = []
        with open(COST_LOG_PATH) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except:
                        continue
        
        # Calculate summary
        total_cost = sum(e.get("cost_usd", 0) for e in entries)
        total_input = sum(e.get("input_tokens", 0) for e in entries)
        total_output = sum(e.get("output_tokens", 0) for e in entries)
        
        # By model
        by_model = {}
        for entry in entries:
            model = entry.get("model", "unknown")
            if model not in by_model:
                by_model[model] = {"count": 0, "cost": 0, "tokens": 0}
            by_model[model]["count"] += 1
            by_model[model]["cost"] += entry.get("cost_usd", 0)
            by_model[model]["tokens"] += entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
        
        return {
            "total_entries": len(entries),
            "total_cost_usd": round(total_cost, 4),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "by_model": by_model
        }
    
    def get_time_cost_analysis(self) -> dict:
        """Get time-cost analysis."""
        # Simplified time-cost analysis
        if not COST_LOG_PATH.exists():
            return {"error": "No cost log available"}
        
        entries = []
        with open(COST_LOG_PATH) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except:
                        continue
        
        # Estimate time cost (simplified)
        hourly_rate = 100
        baseline_tps = 100
        
        total_time_cost = 0
        total_monetary_cost = 0
        
        for entry in entries:
            output_tokens = entry.get("output_tokens", 0)
            cost_usd = entry.get("cost_usd", 0)
            
            # Estimate response time
            response_time_sec = output_tokens / baseline_tps
            time_cost = (response_time_sec / 3600.0) * hourly_rate
            
            total_time_cost += time_cost
            total_monetary_cost += cost_usd
        
        return {
            "hourly_rate_usd": hourly_rate,
            "total_monetary_cost_usd": round(total_monetary_cost, 4),
            "total_time_cost_usd": round(total_time_cost, 4),
            "total_cost_usd": round(total_monetary_cost + total_time_cost, 4),
            "time_cost_percentage": round((total_time_cost / (total_monetary_cost + total_time_cost)) * 100, 1) if (total_monetary_cost + total_time_cost) > 0 else 0
        }


def main():
    port = 8080
    server = HTTPServer(('localhost', port), BillingAPIHandler)
    
    print(f"Billing API server running at http://localhost:{port}")
    print(f"\nAvailable endpoints:")
    print(f"  GET /api/customers           - List all customers")
    print(f"  GET /api/customers/{{id}}    - Get customer details")
    print(f"  GET /api/invoices            - List invoices")
    print(f"  GET /api/invoices/{{month}}  - Get invoices for month")
    print(f"  GET /api/analytics/summary   - Cost analytics")
    print(f"  GET /api/analytics/time-cost - Time-cost analysis")
    print(f"  GET /api/health              - Health check")
    print(f"\nPress Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
