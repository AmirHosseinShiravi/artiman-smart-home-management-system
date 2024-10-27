#!/bin/bash
set -e

# Function to create user and database if they don't exist
create_web_user_and_db() {
    local db=$1
    local user=$2
    local password=$3
    echo "Creating user and database for $user"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        DO
        \$do\$
        BEGIN
           IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$user') THEN
              CREATE USER $user WITH PASSWORD '$password';
           END IF;
        END
        \$do\$;

        SELECT 'CREATE DATABASE $db'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec

        GRANT ALL PRIVILEGES ON DATABASE $db TO $user;
EOSQL
}

create_mqtt_broker_user_and_db_and_tables() {
    local db=$1
    local user=$2
    local password=$3
    echo "Creating user and database for $user"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        DO
        \$do\$
        BEGIN
           IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$user') THEN
              CREATE USER $user WITH PASSWORD '$password';
           END IF;
        END
        \$do\$;

        SELECT 'CREATE DATABASE $db'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec

        GRANT ALL PRIVILEGES ON DATABASE $db TO $user;
        
        -- Connect to the newly created database
        \c $db

        -- Create mqtt_user table if it doesn't exist
        CREATE TABLE IF NOT EXISTS mqtt_user (
            id SERIAL PRIMARY KEY,
            is_superuser BOOLEAN,
            username VARCHAR(100),
            password_hash VARCHAR(100),
            salt VARCHAR(40)
        );

        -- Create ACTION and PERMISSION types if they don't exist
        DO \$\$ BEGIN
            CREATE TYPE ACTION AS ENUM('publish', 'subscribe', 'all');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END \$\$;

        DO \$\$ BEGIN
            CREATE TYPE PERMISSION AS ENUM('allow', 'deny');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END \$\$;

        -- Create mqtt_acl table if it doesn't exist
        CREATE TABLE IF NOT EXISTS mqtt_acl (
            id SERIAL PRIMARY KEY,
            ipaddress VARCHAR(60) NOT NULL DEFAULT '',
            username VARCHAR(255) NOT NULL DEFAULT '',
            clientid VARCHAR(255) NOT NULL DEFAULT '',
            action ACTION,
            permission PERMISSION,
            topic VARCHAR(255) NOT NULL
        );
EOSQL
}

# Create users and databases for each app
create_web_user_and_db "$WEB_DB" "$WEB_DB_USER" "$WEB_DB_PASSWORD"
create_mqtt_broker_user_and_db_and_tables "$MQTT_BROKER_DB" "$MQTT_BROKER_DB_USER" "$MQTT_BROKER_DB_PASSWORD"
