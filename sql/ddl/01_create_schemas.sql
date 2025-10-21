-- create schemas for the ecommerce data pipeline
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- log the creation of schemas
DO $$
BEGIN
    RAISE NOTICE 'Schemas created successfully';
END $$;