#!/bin/bash

set -e

# Check if the DOMAIN variable is set
if [ -z "$DOMAIN" ]; then
    echo "Error: DOMAIN environment variable is not set."
    exit 1
fi

echo "Generating nginx config files..."
envsubst '$DOMAIN' < /etc/nginx/config_templates/toplevel_http_mqtt_config.tpl > /etc/nginx/conf.d/toplevel_http_mqtt_config.conf
envsubst '$DOMAIN' < /etc/nginx/config_templates/toplevel_tcp_stream_mqtt_config.tpl > /etc/nginx/conf.d/toplevel_tcp_stream_mqtt_config.conf

# Execute any additional commands passed to the script
exec "$@"
