-- Create database (safe if already exists)
SELECT 'CREATE DATABASE mydb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mydb')\gexec

-- Create user (safe if already exists)
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'kodekloud'
   ) THEN
      CREATE USER kodekloud WITH PASSWORD 'kkpass123';
   END IF;
END
$$;

-- Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE mydb TO kodekloud;

-- Switch to mydb
\connect mydb

-- Create table
CREATE TABLE IF NOT EXISTS cheque (
  cheque_no VARCHAR(20) PRIMARY KEY,
  approval_granted BOOLEAN NOT NULL
);

-- Grant table privileges
GRANT ALL PRIVILEGES ON TABLE cheque TO kodekloud;
