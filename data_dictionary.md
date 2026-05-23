# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `products.csv` | Product, state, channel | Segment master table for P&C product performance and source ownership. |
| `monthly_product_metrics.csv` | Product segment, month | Monthly trend layer for earned premium, loss ratio, combined ratio, retention, claims satisfaction, and KPI quality. |
| `data_quality_checks.csv` | Product segment, quality check | Governance queue showing source-system, metric, failed-row rate, severity, owner, and remediation status. |
| `market_trends.csv` | Market trend | Analyst context for interpreting product signals in a current P&C operating environment. |
| `stakeholder_requests.csv` | Stakeholder request | Business questions and decision owners for the management brief. |
| `analysis/outputs/product_priority_queue.csv` | Product segment | Ranked queue combining performance pressure, retention risk, growth signal, and data-governance risk. |
| `analysis/outputs/management_action_plan.csv` | Ranked action | Follow-up artifact, owner, and expected business use for each top segment. |
| `analysis/outputs/app_payload.json` | Application payload | Compact JSON consumed by the static workbench UI. |

## Key Metrics

| Metric | Meaning |
|---|---|
| `combined_ratio` | Loss ratio plus expense ratio. A value above 100% indicates underwriting pressure before investment income. |
| `retention_rate` | Modeled policyholder retention for the product segment. |
| `new_business_growth` | Modeled year-over-year growth signal for the segment. |
| `claims_satisfaction` | Synthetic service-quality score shaped by product and claims pressure. |
| `kpi_quality_score` | Synthetic score for completeness, accuracy, timeliness, and ownership readiness. |
| `priority_score` | Transparent weighted rank used to decide which segment needs management attention first. |
