set -e

psql -v ON_ERROR_STOP=1 --username "$DB_USER" --dbname "$DB_NAME" <<-EOSQL
    CREATE DATABASE "$DB_NAME";
    CREATE USER "$DB_USER" WITH ENCRYPTED PASSWORD '"$DB_PASS"';
    GRANT ALL PRIVILEGES ON DATABASE "$DB_USER" TO "$DB_NAME";
EOSQL