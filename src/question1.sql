-- 1. From the two most commonly appearing regions, which is the latest datasource?
WITH top_regions AS (
    SELECT city, COUNT(*) as region_count
    FROM trips
    GROUP BY city
    ORDER BY region_count DESC
    LIMIT 2
)
SELECT 
    t.city,
    t.datasource,
    t.ts
FROM trips t
INNER JOIN top_regions tr ON t.city = tr.city
WHERE t.ts = (
    SELECT MAX(ts)
    FROM trips t2
    WHERE t2.city = t.city
)
ORDER BY t.ts DESC;