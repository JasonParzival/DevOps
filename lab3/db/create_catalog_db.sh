#!/bin/sh
set -eu
# Works with an already initialized PostgreSQL volume from stage 1.
# psql -X prevents loading local client settings.
if [ "$(psql -X -d users_db -Atqc "SELECT count(*) FROM pg_database WHERE datname='catalog_db'")" = "0" ]; then
  psql -X -v ON_ERROR_STOP=1 -d users_db -c 'CREATE DATABASE catalog_db'
  echo 'catalog_db created'
else
  echo 'catalog_db already exists'
fi
