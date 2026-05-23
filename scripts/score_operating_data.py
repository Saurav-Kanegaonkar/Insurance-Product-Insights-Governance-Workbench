import csv
import json
import math
import random
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "analysis" / "outputs"
DOCS_DIR = ROOT / "analysis"
random.seed(91317)


STATES = [
    ("NJ", 1.00, 0.99, 0.94),
    ("PA", 0.94, 0.97, 0.91),
    ("NY", 0.90, 1.06, 0.88),
    ("MD", 0.82, 0.98, 0.86),
    ("DE", 0.70, 0.95, 0.84),
    ("CT", 0.64, 1.01, 0.82),
]

PRODUCTS = [
    ("Personal Auto", "Personal", 0.40, 0.22, 91.0, 0.86, "policy_admin, claims, billing, quote_platform"),
    ("Homeowners", "Personal", 0.23, 0.24, 103.5, 0.88, "policy_admin, claims, catastrophe_vendor, billing"),
    ("Renters", "Personal", 0.08, 0.28, 86.5, 0.91, "policy_admin, billing, customer_portal"),
    ("Personal Umbrella", "Personal", 0.05, 0.18, 82.0, 0.93, "policy_admin, claims, billing"),
    ("Workers Compensation", "Commercial", 0.11, 0.25, 94.5, 0.90, "policy_admin, claims, payroll_audit, agency_feed"),
    ("Commercial Auto", "Commercial", 0.07, 0.26, 108.0, 0.82, "policy_admin, claims, mvr_vendor, agency_feed"),
    ("Businessowners Policy", "Commercial", 0.04, 0.27, 96.0, 0.84, "policy_admin, claims, agency_feed, inspection_vendor"),
    ("Commercial Umbrella", "Commercial", 0.02, 0.19, 100.0, 0.80, "policy_admin, claims, agency_feed"),
]

CHANNELS = [
    ("Direct", 1.00, 0.96),
    ("Exclusive Agent", 0.82, 0.93),
    ("Independent Agent", 0.70, 0.87),
]

MONTHS = [f"2025-{month:02d}-01" for month in range(1, 13)]


def clamp(value, low, high):
    return max(low, min(high, value))


def pct(value):
    return round(value, 1)


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_products():
    rows = []
    product_id = 1
    for product, line, premium_weight, expense_ratio, base_combined, base_retention, sources in PRODUCTS:
        for state, scale, loss_factor, source_readiness in STATES:
            for channel, channel_scale, channel_quality in CHANNELS:
                if line == "Personal" and channel == "Independent Agent":
                    continue
                if line == "Commercial" and channel == "Exclusive Agent":
                    continue
                exposure = int(62000 * premium_weight * scale * channel_scale * random.uniform(0.62, 1.18))
                avg_premium = random.uniform(520, 2050) if line == "Personal" else random.uniform(3200, 14200)
                earned_premium = int(exposure * avg_premium)
                loss_ratio = clamp(base_combined - expense_ratio * 100 + random.gauss(0, 4.2), 48, 91)
                loss_ratio = clamp(loss_ratio * loss_factor + (4.0 if product in {"Homeowners", "Commercial Auto"} else 0), 50, 96)
                combined_ratio = loss_ratio + expense_ratio * 100 + random.gauss(0, 1.8)
                growth = random.gauss(4.6, 5.0) + (3.5 if state in {"PA", "MD", "CT"} else 0)
                if channel == "Independent Agent":
                    growth += random.uniform(2.0, 6.5)
                retention = clamp(base_retention + random.gauss(0, 0.035) - max(combined_ratio - 100, 0) / 400, 0.71, 0.96)
                claims_satisfaction = clamp(92 - max(combined_ratio - 95, 0) * 0.75 + random.gauss(0, 2.6), 72, 98)
                kpi_quality = clamp((source_readiness * channel_quality * 100) + random.gauss(0, 4.5), 62, 99)
                rows.append(
                    {
                        "product_id": f"PRD{product_id:03d}",
                        "product": product,
                        "line_of_business": line,
                        "state": state,
                        "channel": channel,
                        "exposure_count": exposure,
                        "earned_premium": earned_premium,
                        "loss_ratio": pct(loss_ratio),
                        "expense_ratio": pct(expense_ratio * 100),
                        "combined_ratio": pct(combined_ratio),
                        "retention_rate": pct(retention * 100),
                        "new_business_growth": pct(growth),
                        "claims_satisfaction": pct(claims_satisfaction),
                        "kpi_quality_score": pct(kpi_quality),
                        "source_systems": sources,
                        "data_steward": random.choice(["Product Analytics", "Claims Data", "Commercial Lines Ops", "BI Governance"]),
                    }
                )
                product_id += 1
    return rows


def make_monthly_metrics(products):
    rows = []
    for item in products:
        base_premium = int(item["earned_premium"]) / 12
        base_combined = float(item["combined_ratio"])
        base_retention = float(item["retention_rate"])
        base_quality = float(item["kpi_quality_score"])
        for idx, month in enumerate(MONTHS, start=1):
            seasonality = math.sin(idx / 12 * math.pi * 2) * 1.8
            if item["product"] == "Homeowners" and idx in {6, 7, 8, 9}:
                seasonality += 4.5
            if item["product"] in {"Commercial Auto", "Workers Compensation"} and idx in {1, 4, 7, 10}:
                seasonality += 2.2
            premium = int(base_premium * (1 + (idx - 6) * float(item["new_business_growth"]) / 1200) * random.uniform(0.94, 1.07))
            combined_ratio = clamp(base_combined + seasonality + random.gauss(0, 2.6), 70, 124)
            quality_score = clamp(base_quality - random.choice([0, 0, 0, 2.5, 4.0]) + random.gauss(0, 1.6), 58, 99)
            rows.append(
                {
                    "month": month,
                    "product_id": item["product_id"],
                    "earned_premium": premium,
                    "loss_ratio": pct(combined_ratio - float(item["expense_ratio"])),
                    "combined_ratio": pct(combined_ratio),
                    "retention_rate": pct(clamp(base_retention - max(combined_ratio - 100, 0) / 70 + random.gauss(0, 1.1), 65, 98)),
                    "claims_satisfaction": pct(clamp(float(item["claims_satisfaction"]) - max(combined_ratio - 100, 0) / 4 + random.gauss(0, 1.4), 65, 99)),
                    "kpi_quality_score": pct(quality_score),
                }
            )
    return rows


def make_quality_checks(products):
    check_templates = [
        ("Policy count reconciliation", "exposure_count", "policy_admin", "Completeness"),
        ("Claims lag validation", "loss_ratio", "claims", "Timeliness"),
        ("Agency appointment mapping", "channel", "agency_feed", "Accuracy"),
        ("Metric definition owner assigned", "combined_ratio", "semantic_layer", "Governance"),
        ("Catastrophe territory enrichment", "loss_ratio", "catastrophe_vendor", "Completeness"),
        ("Premium transaction duplicate scan", "earned_premium", "billing", "Accuracy"),
    ]
    rows = []
    check_id = 1
    for item in products:
        templates = random.sample(check_templates, 3)
        if item["channel"] == "Independent Agent":
            templates.append(("Agency appointment mapping", "channel", "agency_feed", "Accuracy"))
        if item["product"] == "Homeowners":
            templates.append(("Catastrophe territory enrichment", "loss_ratio", "catastrophe_vendor", "Completeness"))
        for check_name, metric, source, dimension in templates:
            quality = float(item["kpi_quality_score"])
            failure_rate = clamp((100 - quality) / 2.2 + random.gauss(0, 1.8), 0.2, 22)
            severity = "High" if failure_rate >= 12 else "Medium" if failure_rate >= 6 else "Low"
            rows.append(
                {
                    "check_id": f"DQ{check_id:04d}",
                    "product_id": item["product_id"],
                    "check_name": check_name,
                    "impacted_metric": metric,
                    "source_system": source,
                    "quality_dimension": dimension,
                    "failed_row_rate": pct(failure_rate),
                    "severity": severity,
                    "owner": item["data_steward"],
                    "status": random.choice(["Open", "Open", "In Review", "Remediation Planned", "Monitoring"]),
                }
            )
            check_id += 1
    return rows


def make_market_trends():
    return [
        {
            "trend_id": "MKT001",
            "trend": "Personal auto profitability recovery",
            "affected_products": "Personal Auto",
            "modeled_assumption": "Lower combined ratio pressure but more shopping sensitivity as rates stabilize",
            "analyst_response": "Track retention, quote conversion, and claim severity together before recommending rate or discount actions",
        },
        {
            "trend_id": "MKT002",
            "trend": "Homeowners catastrophe volatility",
            "affected_products": "Homeowners",
            "modeled_assumption": "Seasonal weather and replacement-cost uncertainty can move loss ratio faster than premium actions",
            "analyst_response": "Separate weather-driven variance from controllable underwriting or data-definition issues",
        },
        {
            "trend_id": "MKT003",
            "trend": "Commercial auto severity pressure",
            "affected_products": "Commercial Auto",
            "modeled_assumption": "Litigation and repair-cost severity keep casualty lines above target in several markets",
            "analyst_response": "Prioritize account mix, claim severity, and MVR data quality in the monthly product review",
        },
        {
            "trend_id": "MKT004",
            "trend": "Independent agency expansion",
            "affected_products": "Commercial lines",
            "modeled_assumption": "Newer agency channels create growth upside and more source-system mapping risk",
            "analyst_response": "Pair agency production KPIs with appointment, appetite, and source completeness checks",
        },
    ]


def make_requests(products):
    request_topics = [
        ("Management KPI refresh", "Which product/state combinations are above combined-ratio target and why?"),
        ("Agency channel review", "Where is independent agency growth creating source-data mapping risk?"),
        ("Claims service readout", "Which segments show satisfaction decline alongside loss-ratio pressure?"),
        ("Corrective action planning", "Which data fixes are blocking a confident business recommendation?"),
        ("Market scan", "Which industry trends should change the next product review agenda?"),
    ]
    rows = []
    for idx, (topic, question) in enumerate(request_topics, start=1):
        focus = random.choice(products)
        rows.append(
            {
                "request_id": f"REQ{idx:03d}",
                "request_type": topic,
                "business_question": question,
                "primary_product_focus": focus["product"],
                "decision_owner": random.choice(["Product Management", "Commercial Lines", "Claims Leadership", "BI Governance"]),
                "due_in_days": random.choice([3, 5, 7, 10]),
                "status": random.choice(["Ready for review", "Analysis in progress", "Data rule clarification needed"]),
            }
        )
    return rows


def score_products(products, quality_checks):
    failures = defaultdict(float)
    high_checks = defaultdict(int)
    for check in quality_checks:
        failures[check["product_id"]] += float(check["failed_row_rate"])
        if check["severity"] == "High":
            high_checks[check["product_id"]] += 1

    rows = []
    for item in products:
        combined_gap = max(float(item["combined_ratio"]) - 96.0, 0)
        quality_gap = max(92.0 - float(item["kpi_quality_score"]), 0)
        retention_gap = max(88.0 - float(item["retention_rate"]), 0)
        growth_signal = max(float(item["new_business_growth"]), 0) / 2
        channel_multiplier = 1.16 if item["channel"] == "Independent Agent" else 1.0
        priority = (combined_gap * 2.1 + quality_gap * 1.5 + retention_gap * 1.2 + failures[item["product_id"]] * 0.35 + growth_signal) * channel_multiplier
        if item["product"] in {"Homeowners", "Commercial Auto"}:
            priority += 7
        action = "Validate source rules before management action"
        if combined_gap > 10 and quality_gap < 7:
            action = "Prepare corrective product recommendation"
        if quality_gap > 12:
            action = "Open data governance remediation"
        if item["channel"] == "Independent Agent" and growth_signal > 4:
            action = "Review agency growth with source mapping"
        rows.append(
            {
                "product_id": item["product_id"],
                "product": item["product"],
                "line_of_business": item["line_of_business"],
                "state": item["state"],
                "channel": item["channel"],
                "earned_premium": item["earned_premium"],
                "combined_ratio": item["combined_ratio"],
                "retention_rate": item["retention_rate"],
                "new_business_growth": item["new_business_growth"],
                "claims_satisfaction": item["claims_satisfaction"],
                "kpi_quality_score": item["kpi_quality_score"],
                "open_high_quality_checks": high_checks[item["product_id"]],
                "priority_score": pct(priority),
                "recommended_action": action,
            }
        )
    return sorted(rows, key=lambda row: float(row["priority_score"]), reverse=True)


def make_action_plan(priority_queue):
    rows = []
    for idx, item in enumerate(priority_queue[:24], start=1):
        if item["recommended_action"].startswith("Open data"):
            owner = "BI Governance"
            artifact = "DQ remediation ticket and metric-definition note"
            expected = "Raise KPI trust score before management readout"
        elif item["recommended_action"].startswith("Prepare"):
            owner = "Product Management"
            artifact = "Product action brief with trend and profitability drivers"
            expected = "Create corrective action recommendation for next operating review"
        elif "agency" in item["recommended_action"].lower():
            owner = "Commercial Lines Ops"
            artifact = "Agency channel source-mapping review"
            expected = "Separate growth opportunity from source-system noise"
        else:
            owner = "Product Analytics"
            artifact = "Source-rule validation summary"
            expected = "Confirm whether the KPI signal is decision-ready"
        rows.append(
            {
                "rank": idx,
                "product_id": item["product_id"],
                "management_question": f"Can we act on the {item['product']} signal in {item['state']} via {item['channel']}?",
                "owner": owner,
                "next_artifact": artifact,
                "expected_business_use": expected,
            }
        )
    return rows


def aggregate_summary(products, priority_queue, checks):
    total_premium = sum(int(row["earned_premium"]) for row in products)
    weighted_combined = sum(float(row["combined_ratio"]) * int(row["earned_premium"]) for row in products) / total_premium
    weighted_quality = sum(float(row["kpi_quality_score"]) * int(row["earned_premium"]) for row in products) / total_premium
    high_checks = sum(1 for row in checks if row["severity"] == "High")
    top = priority_queue[0]
    return {
        "generated_on": date.today().isoformat(),
        "product_segments": len(products),
        "monthly_metric_rows": len(products) * len(MONTHS),
        "earned_premium": total_premium,
        "weighted_combined_ratio": round(weighted_combined, 1),
        "weighted_kpi_quality": round(weighted_quality, 1),
        "high_quality_checks": high_checks,
        "top_priority": top,
    }


def write_docs(summary, priority_queue):
    findings = f"""# Executive Findings

The workbench flags {summary['product_segments']} synthetic P&C product, state, and channel segments and ranks them by combined-ratio pressure, retention risk, KPI trust, and source-data readiness.

## Headline

The highest-priority segment is {summary['top_priority']['product']} in {summary['top_priority']['state']} through {summary['top_priority']['channel']}. It has a priority score of {summary['top_priority']['priority_score']}, a combined ratio of {summary['top_priority']['combined_ratio']}%, and a KPI quality score of {summary['top_priority']['kpi_quality_score']}.

## What management should ask

1. Is the result a real product performance issue, a source-data issue, or both?
2. Which KPI definition or source mapping must be clarified before a dashboard refresh?
3. Which corrective action belongs in the next product operating review?

## Recommended cadence

Use the executive cockpit for the weekly management readout, the diagnostic view for the "why" conversation, and the governance queue for Data Engineer and business-process follow-up.
"""
    plan = """# Analysis Plan

1. Load synthetic product, monthly metric, governance, market trend, and stakeholder request tables.
2. Calculate product-level combined-ratio pressure, retention risk, new-business signal, claims satisfaction, and KPI quality.
3. Join data-quality checks to product segments so business recommendations are separated from source remediation.
4. Rank product segments with a transparent weighted score.
5. Produce a management action plan and SQL validation examples.
"""
    sql = """-- T-SQL style validation checks for the portfolio artifact.
-- Tables mirror the synthetic CSVs generated in /data.

-- 1. Product KPI rollup for a Power BI or SSRS semantic model.
SELECT
    p.product,
    p.line_of_business,
    p.state,
    p.channel,
    SUM(m.earned_premium) AS earned_premium,
    AVG(m.combined_ratio) AS avg_combined_ratio,
    AVG(m.retention_rate) AS avg_retention_rate,
    AVG(m.kpi_quality_score) AS avg_kpi_quality_score
FROM dbo.products p
JOIN dbo.monthly_product_metrics m
    ON p.product_id = m.product_id
GROUP BY
    p.product,
    p.line_of_business,
    p.state,
    p.channel;

-- 2. Segments where business action should wait for source remediation.
SELECT
    p.product,
    p.state,
    p.channel,
    q.check_name,
    q.impacted_metric,
    q.failed_row_rate,
    q.owner
FROM dbo.products p
JOIN dbo.data_quality_checks q
    ON p.product_id = q.product_id
WHERE q.severity = 'High'
ORDER BY q.failed_row_rate DESC;

-- 3. Management priority queue, combining performance and governance signals.
SELECT TOP 15
    r.product,
    r.state,
    r.channel,
    r.priority_score,
    r.combined_ratio,
    r.kpi_quality_score,
    r.recommended_action
FROM dbo.product_priority_queue r
ORDER BY r.priority_score DESC;
"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "executive_findings.md").write_text(findings)
    (DOCS_DIR / "analysis_plan.md").write_text(plan)
    (DOCS_DIR / "sql_checks.sql").write_text(sql)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    products = make_products()
    monthly = make_monthly_metrics(products)
    quality_checks = make_quality_checks(products)
    market_trends = make_market_trends()
    requests = make_requests(products)
    priority_queue = score_products(products, quality_checks)
    action_plan = make_action_plan(priority_queue)
    summary = aggregate_summary(products, priority_queue, quality_checks)

    write_csv(DATA_DIR / "products.csv", products, list(products[0].keys()))
    write_csv(DATA_DIR / "monthly_product_metrics.csv", monthly, list(monthly[0].keys()))
    write_csv(DATA_DIR / "data_quality_checks.csv", quality_checks, list(quality_checks[0].keys()))
    write_csv(DATA_DIR / "market_trends.csv", market_trends, list(market_trends[0].keys()))
    write_csv(DATA_DIR / "stakeholder_requests.csv", requests, list(requests[0].keys()))

    write_csv(OUTPUT_DIR / "product_priority_queue.csv", priority_queue, list(priority_queue[0].keys()))
    write_csv(OUTPUT_DIR / "management_action_plan.csv", action_plan, list(action_plan[0].keys()))
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUTPUT_DIR / "app_payload.json").write_text(
        json.dumps(
            {
                "summary": summary,
                "priorityQueue": priority_queue[:25],
                "qualityQueue": sorted(quality_checks, key=lambda row: float(row["failed_row_rate"]), reverse=True)[:35],
                "marketTrends": market_trends,
                "stakeholderRequests": requests,
                "actionPlan": action_plan,
            },
            indent=2,
        )
    )
    write_docs(summary, priority_queue)

    print(
        f"Generated {len(products)} product segments, {len(monthly)} monthly rows, "
        f"{len(quality_checks)} data-quality checks, and {len(priority_queue)} ranked priorities."
    )
    print(
        f"Top priority: {summary['top_priority']['product']} {summary['top_priority']['state']} "
        f"{summary['top_priority']['channel']} score={summary['top_priority']['priority_score']}"
    )


if __name__ == "__main__":
    main()
