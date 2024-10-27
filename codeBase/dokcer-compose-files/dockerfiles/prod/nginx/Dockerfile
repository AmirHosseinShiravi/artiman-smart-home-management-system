FROM nginxproxy/nginx-proxy

COPY vhost.d/default /etc/nginx/vhost.d/default
COPY custom.conf /etc/nginx/conf.d/custom.conf
COPY toplevel_http_mqtt_config.conf /etc/nginx/conf.d/toplevel_http_mqtt_config.conf
COPY toplevel_tcp_stream_mqtt_config.conf /etc/nginx/toplevel.conf.d/toplevel_tcp_stream_mqtt_config.conf