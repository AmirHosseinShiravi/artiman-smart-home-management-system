FROM nginxproxy/nginx-proxy

COPY vhost.d/default /etc/nginx/vhost.d/default
COPY custom.conf /etc/nginx/conf.d/custom.conf

# COPY toplevel_http_mqtt_config.tpl /etc/nginx/config_templates/toplevel_http_mqtt_config.tpl
# RUN envsubst < /etc/nginx/config_templates/toplevel_http_mqtt_config.tpl > /etc/nginx/conf.d/toplevel_http_mqtt_config.conf


# RUN envsubst < /etc/nginx/config_templates/toplevel_tcp_stream_mqtt_config.tpl > /etc/nginx/toplevel.conf.d/toplevel_tcp_stream_mqtt_config.conf


COPY ./config/toplevel_http_mqtt_config.conf /etc/nginx/conf.d/toplevel_http_mqtt_config.conf
COPY ./config/toplevel_tcp_stream_mqtt_config.conf /etc/nginx/toplevel.conf.d/toplevel_tcp_stream_mqtt_config.conf

# to access to nc command 
RUN apt-get update
RUN apt install -y netcat-openbsd 


# COPY ./config/* /etc/nginx/config_templates/
# COPY ./entrypoint.sh /etc/nginx/config_templates/entrypoint.sh

# RUN chmod +x /etc/nginx/config_templates/entrypoint.sh


# CMD ["/etc/nginx/config_templates/entrypoint.sh"]

