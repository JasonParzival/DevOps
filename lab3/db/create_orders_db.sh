#!/bin/sh
set -eu
if [ "$(psql -X -d users_db -Atqc "SELECT count(*) FROM pg_database WHERE datname='orders_db'")" = "0" ]; then
  psql -X -v ON_ERROR_STOP=1 -d users_db -c 'CREATE DATABASE orders_db'
  echo 'orders_db created'
else
  echo 'orders_db already exists'
fi
