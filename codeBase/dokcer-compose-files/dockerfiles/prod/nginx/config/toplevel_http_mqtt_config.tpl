
  # Nginx status
  server {
    listen 8888;
    
    location /status {            
      stub_status on;            
      access_log off;            
    }
  }

  upstream emqxws {
    server emqx-mqtt-broker:8083;
    # server emqx2-cluster.emqx.io:8083;
    # server emqx3-cluster.emqx.io:8083;
  }
  
  # ws
  server {
    listen 8083;

    location /mqtt {
        proxy_pass http://emqxws;
        
        # websocket连接的Upgrade必须设置为WebSocket，表示在取得服务器响应之后，使用HTTP升级将HTTP协议转换(升级)为WebSocket协议            
        proxy_set_header Upgrade $http_upgrade;            
        # websocket 的Connection必须设置为Upgrade，表示客户端希望连接升级            
        proxy_set_header Connection "Upgrade";            
        #反向代理真实IP            
        proxy_set_header Host $host;            
        proxy_set_header X-Real-IP $remote_addr;            
        proxy_set_header REMOTE-HOST $remote_addr;            
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;              
        #禁用缓存             
        proxy_buffering off;
    }
  }

  # wss
  server {
    listen 8084 ssl;

    access_log /var/log/nginx/access.log vhost;
    ssl_session_timeout 5m;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_certificate /etc/nginx/certs/${DOMAIN}.crt;
    ssl_certificate_key /etc/nginx/certs/${DOMAIN}.key;
    ssl_dhparam /etc/nginx/certs/${DOMAIN}.dhparam.pem;
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/nginx/certs/${DOMAIN}.chain.pem;
    set $sts_header "";
    if ($https) {
        set $sts_header "max-age=31536000";
    }
    add_header Strict-Transport-Security $sts_header always;

    location /mqtt {
        proxy_pass http://emqxws;

        # WebSocket Connection Upgrade must be set to "WebSocket," indicating that after receiving a server response, the HTTP protocol is transformed (upgraded) to the WebSocket protocol.
        proxy_set_header Upgrade $http_upgrade;            
        # WebSocket Connection header must be set to "Upgrade," indicating that the client wishes to upgrade the connection.            
        proxy_set_header Connection "Upgrade";            
        # Proxy Real IP     
        proxy_set_header Host $host;            
        proxy_set_header X-Real-IP $remote_addr;            
        proxy_set_header REMOTE-HOST $remote_addr;            
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;              
        # Disable Caching         
        proxy_buffering off;
    }
  }
