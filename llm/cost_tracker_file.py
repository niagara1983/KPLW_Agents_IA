"""
Cost Tracker - File-based persistence for API costs
Maintains running total across all RFP runs
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class CostTrackerFile:
    """Track and persist API costs across all runs."""

    def __init__(self, cost_file: str = "costs_history.json"):
        """
        Initialize cost tracker with file persistence.

        Args:
            cost_file: Path to JSON file for storing cost history
        """
        self.cost_file = Path(cost_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create cost file if it doesn't exist."""
        if not self.cost_file.exists():
            initial_data = {
                "total_cost": 0.0,
                "total_calls": 0,
                "runs": []
            }
            self._save_data(initial_data)

    def _load_data(self) -> dict:
        """Load cost data from file."""
        try:
            with open(self.cost_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load cost file: {e}")
            return {"total_cost": 0.0, "total_calls": 0, "runs": []}

    def _save_data(self, data: dict):
        """Save cost data to file."""
        try:
            with open(self.cost_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Could not save cost file: {e}")

    def add_run(
        self,
        project_id: str,
        rfp_name: str,
        cost_summary: Dict,
        agent_costs: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Add a new RFP run to cost history.

        Args:
            project_id: Project identifier (e.g., RFP-20260207-213332)
            rfp_name: Name of the RFP document
            cost_summary: Cost summary from LLMClient
            agent_costs: Optional breakdown by agent (TIMBO, ZAT, MARY, RANA)
            metadata: Optional additional info (template, iterations, score, etc.)
        """
        data = self._load_data()

        run_cost = cost_summary.get('total_cost', 0.0)
        run_calls = cost_summary.get('num_calls', 0)

        # Create run record
        run_record = {
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "rfp_name": rfp_name,
            "cost": run_cost,
            "calls": run_calls,
            "agent_costs": agent_costs or {},
            "metadata": metadata or {}
        }

        # Update totals
        data["total_cost"] += run_cost
        data["total_calls"] += run_calls
        data["runs"].append(run_record)

        # Save
        self._save_data(data)

        # Print summary
        print(f"\n  💰 Cost tracking updated:")
        print(f"     This run: ${run_cost:.4f} ({run_calls} calls)")
        print(f"     Total accumulated: ${data['total_cost']:.4f} ({data['total_calls']} calls)")
        print(f"     Saved to: {self.cost_file}")

    def get_total(self) -> Dict:
        """
        Get total accumulated costs.

        Returns:
            Dictionary with total_cost, total_calls, run_count
        """
        data = self._load_data()
        return {
            "total_cost": data.get("total_cost", 0.0),
            "total_calls": data.get("total_calls", 0),
            "run_count": len(data.get("runs", []))
        }

    def get_runs(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get recent runs.

        Args:
            limit: Maximum number of runs to return (most recent first)

        Returns:
            List of run records
        """
        data = self._load_data()
        runs = data.get("runs", [])

        # Sort by timestamp (most recent first)
        runs_sorted = sorted(runs, key=lambda x: x.get("timestamp", ""), reverse=True)

        if limit:
            return runs_sorted[:limit]
        return runs_sorted

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a cost report.

        Args:
            output_path: Optional path to save report as markdown

        Returns:
            Report as markdown string
        """
        data = self._load_data()
        total_cost = data.get("total_cost", 0.0)
        total_calls = data.get("total_calls", 0)
        runs = data.get("runs", [])

        # Build report
        report = []
        report.append("# KPLW RFP System - Cost Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        report.append("## Summary\n")
        report.append(f"- **Total Cost:** ${total_cost:.4f} USD")
        report.append(f"- **Total API Calls:** {total_calls:,}")
        report.append(f"- **Total Runs:** {len(runs)}")
        if runs:
            avg_cost = total_cost / len(runs)
            report.append(f"- **Average Cost per Run:** ${avg_cost:.4f}")
        report.append("")

        # Recent runs
        report.append("## Recent Runs (Last 10)\n")
        report.append("| Date | Project ID | RFP | Cost | Calls | Score |")
        report.append("|------|-----------|-----|------|-------|-------|")

        for run in sorted(runs, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]:
            date = run.get("timestamp", "")[:10]
            project_id = run.get("project_id", "N/A")
            rfp_name = run.get("rfp_name", "N/A")[:30]
            cost = run.get("cost", 0.0)
            calls = run.get("calls", 0)
            score = run.get("metadata", {}).get("rana_score", "N/A")

            report.append(f"| {date} | {project_id} | {rfp_name} | ${cost:.4f} | {calls} | {score} |")

        report.append("")

        # Agent breakdown (if available)
        agent_totals = {}
        for run in runs:
            agent_costs = run.get("agent_costs", {})
            for agent, cost in agent_costs.items():
                agent_totals[agent] = agent_totals.get(agent, 0.0) + cost

        if agent_totals:
            report.append("## Cost by Agent\n")
            report.append("| Agent | Total Cost | Percentage |")
            report.append("|-------|-----------|------------|")
            for agent, cost in sorted(agent_totals.items(), key=lambda x: x[1], reverse=True):
                pct = (cost / total_cost * 100) if total_cost > 0 else 0
                report.append(f"| {agent} | ${cost:.4f} | {pct:.1f}% |")
            report.append("")

        # Budget warnings
        report.append("## Budget Status\n")
        budget_limit = float(os.getenv("BUDGET_LIMIT_USD", "100.0"))
        if total_cost >= budget_limit * 0.9:
            report.append(f"⚠️ **WARNING:** Approaching budget limit (${total_cost:.2f} / ${budget_limit:.2f})")
        else:
            remaining = budget_limit - total_cost
            report.append(f"✅ Budget remaining: ${remaining:.2f} / ${budget_limit:.2f}")

        report_text = "\n".join(report)

        # Save to file if requested
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"  📊 Cost report saved to: {output_path}")

        return report_text

    def reset(self):
        """Reset all cost tracking (use with caution!)."""
        initial_data = {
            "total_cost": 0.0,
            "total_calls": 0,
            "runs": []
        }
        self._save_data(initial_data)
        print("  ⚠️  Cost tracking reset to zero")
