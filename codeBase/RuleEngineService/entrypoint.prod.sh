#!/bin/sh

echo "Waiting for EMQX Broker..."

    while ! nc -z $EMQX_HOST $EMQX_PORT; do
      sleep 0.1
    done

    echo "EMQX Broker started"



envsubst < /home/app/RuleEngineService/config.tpl > /home/app/RuleEngineService/config.yml
chown -R app:app /home/app/RuleEngineService

# These commands get permission denied error
# cp -r /home/app/web/venv/Lib/site-packages/eascheduler /usr/local/lib/python3.9/site-packages/eascheduler
# cp -r /home/app/web/venv/Lib/site-packages/pendulum /usr/local/lib/python3.9/site-packages/pendulum

exec "$@"