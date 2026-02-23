-- Table de faits : Relevés de prix
CREATE TABLE fact_fuel_price (
    fact_id SERIAL PRIMARY KEY,
    station_id INT NOT NULL,
    fuel_id INT NOT NULL,
    date_id INT NOT NULL,
    price_value NUMERIC(5, 3),
    update_time TIMESTAMP,
    
    CONSTRAINT fk_station FOREIGN KEY (station_id) REFERENCES dim_station (station_id),
    CONSTRAINT fk_fuel FOREIGN KEY (fuel_id) REFERENCES dim_fuel (fuel_id),
    CONSTRAINT fk_date FOREIGN KEY (date_id) REFERENCES dim_date (date_id),
    
    CONSTRAINT unique_price_reading UNIQUE (station_id, fuel_id, update_time)
);