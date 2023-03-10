user nginx;
worker_processes 1;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  log_format main '{{ log_pattern }}';

  access_log /var/log/nginx/access.log main;

  sendfile on;

  keepalive_timeout 65;
  include /etc/nginx/conf.d/*.conf;

}
