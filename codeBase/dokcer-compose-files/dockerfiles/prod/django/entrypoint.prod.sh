#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "Waiting for EMQX Broker..."

    while ! nc -z $EMQX_HOST $EMQX_PORT; do
      sleep 0.1
    done

    echo "EMQX Broker started"



envsubst < config.tpl > config.yml
chown -R app:app /home/app/RuleEngineService


exec "$@"