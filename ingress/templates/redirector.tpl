{% if with_ssl %}

server {
# Listen on plain old HTTP and catch all requests so they can be redirected
# to HTTPS instead.
listen 80 default_server reuseport;
listen [::]:80 default_server reuseport;

# Anything requesting this particular URL should be served content from
# Certbot's folder so the HTTP-01 ACME challenges can be completed for the
# HTTPS certificates.
location '/.well-known/acme-challenge' {
    default_type "text/plain";
    root /var/www/letsencrypt;
}

# Everything else gets shunted over to HTTPS for each user defined
# server to handle.
location / {
    return 307 https://$http_host$request_uri;
}
}
{% endif %}