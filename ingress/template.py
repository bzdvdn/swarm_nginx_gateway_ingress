import os

from jinja2 import Template

from values import DEFAULT_LOG_FORMAT, JSON_LOG_FORMAT


def resolve_pattern(pattern: str) -> str:
    log_map = {
        'json': JSON_LOG_FORMAT,
        'default': DEFAULT_LOG_FORMAT,
        'custom': os.environ.get("CUSTOM_LOG_FORMAT", DEFAULT_LOG_FORMAT),
    }
    return log_map.get(pattern) or DEFAULT_LOG_FORMAT


def write_redirector_template():
    redirector_tamplate_path = '/ingress/templates/redirector.tpl'
    redirector_config_path = '/etc/nginx/conf.d/redirector.conf'
    with open(redirector_tamplate_path, 'r') as f:
        redirector_tamplate = f.read()
    redirector_conf = Template(redirector_tamplate, trim_blocks=True).render(
        with_ssl=True,
    )
    with open(redirector_config_path, 'w') as f:
        f.write(redirector_conf)


def write_nginx_conf():
    nginx_tamplate_path = '/ingress/templates/nginx.tpl'
    nginx_config_path = '/etc/nginx/nginx.conf'
    with open(nginx_tamplate_path, 'r') as f:
        nginx_tamplate = f.read()
    redirector_conf = Template(nginx_tamplate, trim_blocks=True).render(
        log_pattern=resolve_pattern(os.environ['LOG_FORMAT']),
    )
    with open(nginx_config_path, 'w') as f:
        f.write(redirector_conf)


def write_gateway_conf(
    nginx_config_template: str,
    servers: dict,
    request_id: bool,
    with_ssl: bool,
) -> str:
    new_gateway_config = Template(nginx_config_template).render(
        servers=servers,
        request_id=request_id,
        with_ssl=with_ssl,
    )
    return new_gateway_config


def handle_gateway_template(
    servers: dict,
    request_id: bool,
    with_ssl: bool,
    debug: bool = False,
) -> bool:
    gateway_config_template_path = '/ingress/templates/gateway.tpl'
    gateway_config_path = '/etc/nginx/conf.d/gateway.conf'

    try:
        with open(gateway_config_path, 'r') as f:
            current_gateway_config = f.read()
    except FileNotFoundError:
        current_gateway_config = ''

    with open(gateway_config_template_path, 'r') as f:
        nginx_config_template = f.read()

    new_gateway_config = write_gateway_conf(
        nginx_config_template=nginx_config_template,
        servers=servers,
        request_id=request_id,
        with_ssl=with_ssl,
    )
    if current_gateway_config != new_gateway_config:

        current_gateway_config = new_gateway_config
        print(
            "[Ingress Auto Configuration] Services have changed, updating nginx configuration..."
        )
        with open(gateway_config_path, 'w') as f:
            f.write(new_gateway_config)
        if debug:
            print(new_gateway_config)
        return True
    return False
