
stream {

  upstream emqxtcp {
    server emqx-mqtt-broker:1883;
  }

  upstream emqxtls {
    # weight

    # down: Indicates that the current server is temporarily excluded from load balancing.
    # weight: Default is 1, where higher weight results in a larger load share.
    # max_fails: Maximum number of allowed request failures; defaults to 1.
    # fail_timeout: Timeout after which failures are considered; default is 10 seconds. After reaching max_fails failures, the server is paused.
    # backup: When other non-backup servers are down or busy, requests are sent to the backup server.
    
    server emqx-mqtt-broker:1883;
    # server emqx1-cluster.emqx.io:1883 weight=1 max_fails=2 ;
    # server emqx2-cluster.emqx.io:1883 weight=1 max_fails=2 down;
    # server emqx3-cluster.emqx.io:1883 weight=2 max_fails=2; 
  }

  # 多网卡
  # split_clients "$remote_addr$remote_port" $multi_ip {        
  #   20% 10.211.55.5;        
  #   20% 10.211.55.20;        
  #   20% 10.211.55.21;        
  #   20% 10.211.55.22;        
  #   * 10.211.55.23;    
  # }

  # TCP
  server {
    listen 1883;
    # Multiple Network Interfaces
    #proxy_bind $multi_ip;

    proxy_pass emqxtcp;
    # EMQX corresponding listeners need to enable the proxy protocol.
    proxy_protocol on;
  }

  # TLS
  server {
    listen 8883 ssl; 

    
    # If the certificate doesn't match the hostname, validation needs to be disabled.
    ssl_verify_client off;
    ssl_verify_depth 0;

    ssl_certificate /etc/nginx/certs/${DOMAIN}.crt;
    ssl_certificate_key /etc/nginx/certs/${DOMAIN}.key;
    ssl_dhparam /etc/nginx/certs/${DOMAIN}.dhparam.pem;

    ssl_trusted_certificate /etc/nginx/certs/${DOMAIN}.chain.pem;
    
    ssl_handshake_timeout 15s;

    proxy_pass emqxtls;
    proxy_buffer_size 4k;

     # EMQX corresponding listeners need to enable the proxy protocol.
    proxy_protocol on;
  }

}
