CREATE MATERIALIZED VIEW mv_monthly_avg_price AS
SELECT 
    d.year,
    d.month,
    s.dept_code,
    f.fuel_name,
    AVG(fp.price_value) as avg_price
FROM fact_fuel_price fp
JOIN dim_date d ON fp.date_id = d.date_id
JOIN dim_station s ON fp.station_id = s.station_id
JOIN dim_fuel f ON fp.fuel_id = f.fuel_id
GROUP BY d.year, d.month, s.dept_code, f.fuel_name;

CREATE INDEX idx_mv_filter ON mv_monthly_avg_price(year, dept_code, fuel_name);