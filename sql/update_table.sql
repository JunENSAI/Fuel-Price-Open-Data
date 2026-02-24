ALTER TABLE fact_fuel_price ALTER COLUMN price_value TYPE NUMERIC(10,3);

-- 1. Correction des prix trop petits (le cas des milliemes devenus 0.001)
UPDATE fact_fuel_price
SET price_value = price_value * 1000
WHERE price_value < 0.5 AND price_value > 0;

-- 2. Correction des prix trop grands (les anciens format 1000+)
UPDATE fact_fuel_price
SET price_value = price_value / 1000
WHERE price_value > 10;
