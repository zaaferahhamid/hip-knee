import duckdb

query = """
SELECT
    State,
    COUNT(*)                                              AS hospitals,
    COUNT(Score)                                          AS with_rate,
    ROUND(100.0 * COUNT(Score) / COUNT(*), 0)             AS pct_reporting,
    ROUND(AVG(Score), 2)                                  AS mean_rate_pct,
    ROUND(SUM(Score * Denominator) / SUM(Denominator), 2) AS weighted_rate_pct,
    SUM(Denominator)                                      AS total_cases
FROM 'data/processed/hip_knee_hospital.csv'
GROUP BY State
HAVING COUNT(Score) >= 10
ORDER BY weighted_rate_pct DESC
"""

result = duckdb.sql(query).df()
print(result.to_string(index=False))
print("\nStates shown:", len(result))