{% for server_name, server in servers.items() %}
server {
    # Docker DNS
    resolver 127.0.0.11;
    server_name {{ server_name }};
    
    {% if server.with_ssl -%}
    listen 443 ssl;

    ssl_certificate         /etc/letsencrypt/live/{{ server_name  }}/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/{{ server_name  }}/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/{{ server_name  }}/chain.pem;
    {% else %}
    listen 80 {{ server_name }} reuseport;
    listen [::]:80 {{ server_name }} reuseport;
    {% endif %}
    {% for service in server.proxies_service_list %}
        location {{ service.location }} {
          {% if service.custom_location_data%}
          {% for custom in service.custom_location_data %}
            {{ custom }};
          {% endfor%}
          {% else %}
              {% if service.rewrites %}
              {% for rewrite  in service.rewrites%}
                {{ rewrite }};
              {% endfor %}
              {% elif service.rewrite_append_slash %}
              rewrite ^(/.*[^/])$ $1/ permanent;
              {% endif %}
              {% if request_id -%}
              proxy_set_header Request-Id $request_id;
              add_header Request-Id $request_id;
              {% endif %}
              proxy_pass_request_headers {{ service.proxy_pass_request_headers }};
              {% for header, value in service.proxy_set_header.items() %}
              proxy_set_header {{ header }} {{ value }};
              {% endfor%}
              proxy_redirect {{service.proxy_redirect}};
              {% if service.proxy_pass_append_uri %}
              proxy_pass "http://{{ service.service_name }}:{{ service.port }}$uri"
              {% else %}
              proxy_pass "http://{{ service.service_name }}:{{ service.port }}";
              {% endif %}
          {% endif %}
        }
    {% endfor %}
    
  }
{% endfor %}