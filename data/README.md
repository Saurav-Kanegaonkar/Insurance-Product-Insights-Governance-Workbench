# Data Sources

This folder contains deterministic synthetic data for a public P&C insurance business-insights portfolio artifact. The data does not represent real carrier performance, policyholder records, claims, agents, premiums, or source-system exports.

The generator models common property and casualty structures:

- Personal and commercial product lines.
- Regional state expansion across NJ, PA, NY, MD, DE, and CT.
- Direct, exclusive-agent, and independent-agent channels.
- KPI themes such as combined ratio, retention, claims satisfaction, new business growth, data completeness, data accuracy, timeliness, and metric ownership.
- Source-system patterns across policy administration, claims, billing, agency feeds, catastrophe enrichment, MVR vendors, inspection vendors, and semantic-layer governance.

## Files

- `products.csv`: Product, state, and channel segment table with exposure, premium, KPI, source-system, and owner fields.
- `monthly_product_metrics.csv`: Monthly KPI history by product segment.
- `data_quality_checks.csv`: Synthetic source validation checks mapped to products, metrics, source systems, dimensions, owners, and remediation status.
- `market_trends.csv`: Modeled public-market context used to frame the management story.
- `stakeholder_requests.csv`: Example business questions that the analyst workbench is designed to answer.

Run `python3 scripts/score_operating_data.py` to regenerate every data file and analysis output.
