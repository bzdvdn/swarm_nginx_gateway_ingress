import os
import time

from docker import Client

from values import TRUE_VALUES
from ssl_certs import generate_letsencrypt_certs
from template import (
    handle_gateway_template,
    write_redirector_template,
    write_nginx_conf,
)
from reload_nginx import reload_nginx
from gateway import GatewayManager


def get_servers(cli: Client) -> dict:
    services = cli.services()
    gateway_manager = GatewayManager(services)
    servers = gateway_manager.get_servers()
    return servers


def main():
    cli = Client(base_url=os.environ['DOCKER_HOST'])
    update_interval = os.environ['UPDATE_INTERVAL']
    renewal_timestamp = 0
    init_app = True
    while True:
        servers = get_servers(cli)
        with_ssl = any(server['with_ssl'] for server in servers.values())
        if init_app:
            write_nginx_conf()
            init_app = False
        if with_ssl and int(time.time()) >= renewal_timestamp:
            if renewal_timestamp == 0:
                write_redirector_template()
                reload_nginx()
                time.sleep(5)
            renewal_timestamp = generate_letsencrypt_certs(
                domains=[domain for domain in servers]
            )
            reload_nginx()
            time.sleep(5)
        reload_conf = handle_gateway_template(
            servers=servers,
            request_id=os.environ['USE_REQUEST_ID'] in TRUE_VALUES,
            with_ssl=with_ssl,
            debug=os.environ['DEBUG'] in TRUE_VALUES,
        )
        print('reload_conf - ', reload_conf)
        # Reload nginx with the new configuration
        if reload_conf:
            reload_nginx()

        time.sleep(int(update_interval))


if __name__ == '__main__':
    main()
