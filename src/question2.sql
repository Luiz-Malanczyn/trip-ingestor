-- 2. What regions has the "cheap_mobile" datasource appeared in?
SELECT DISTINCT city
FROM trips
WHERE datasource = 'cheap_mobile'
ORDER BY city;