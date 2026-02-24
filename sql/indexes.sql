ALTER TABLE dim_station ADD COLUMN IF NOT EXISTS dept_code VARCHAR(3);

UPDATE dim_station 
SET dept_code = SUBSTRING(postal_code FROM 1 FOR 2)
WHERE dept_code IS NULL;

CREATE INDEX idx_station_dept ON dim_station(dept_code);

CREATE INDEX idx_fact_date ON fact_fuel_price(date_id);

CREATE INDEX idx_fact_fuel ON fact_fuel_price(fuel_id);

CREATE INDEX idx_fact_station ON fact_fuel_price(station_id);

CREATE INDEX idx_fact_date_fuel ON fact_fuel_price(date_id, fuel_id);