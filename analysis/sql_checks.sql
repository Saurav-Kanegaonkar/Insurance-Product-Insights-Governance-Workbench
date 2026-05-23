-- T-SQL style validation checks for the portfolio artifact.
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
