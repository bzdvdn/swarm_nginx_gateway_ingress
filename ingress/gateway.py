from values import (
    TRUE_VALUES,
    DEFAULT_PROXY_SET_HEADER,
    DEFAULT_PROXY_REDIRECT,
    DEFAULT_PROXY_REQUEST_HEADER,
    DEFAULT_PROXY_FOR_SERVER,
)
from utils import parse_dotnames_to_dict


class GatewayManager(object):
    def __init__(self, services: list):
        self.services = services

    def parse_service_labels(self, service: dict) -> dict:
        spec_labels: dict = service['Spec'].get('Labels', {})
        result = parse_dotnames_to_dict(spec_labels)
        return result

    def parse_services_labeles(self) -> dict:
        services_labels = {}
        for service in self.services:
            parsed_labels = self.parse_service_labels(service)
            services_labels[service['Spec']['Name']] = parsed_labels
        return services_labels

    def _generate_rewrites(self, rewrites_row: str) -> list:
        splitted = rewrites_row.split(';')
        result = []
        for rewrite in splitted:
            rewrite = rewrite.replace('\n', '')
            if not rewrite:
                continue
            if 'rewrite' not in rewrite:
                value = f'rewrite {rewrite}'.replace('\n', '').strip()
            else:
                value = rewrite.replace('\n', '').strip()
            result.append(value)
        return result

    def _generate_custom_location_data(self, custom_location_data_raw: str) -> list:
        splitted = custom_location_data_raw.split(';')
        result = [row.replace('\n', '').strip() for row in splitted if row != '\n']
        return result

    def get_servers(self):
        servers = {}
        proxies = self.get_proxies()
        for proxy in proxies:
            server_name = proxy['domain_name']
            with_ssl = True if server_name != 'default_server' else False
            if server_name in servers:
                servers[server_name]['proxies_service_list'].append(proxy)
                servers[server_name]['with_ssl'] = with_ssl
            else:
                servers[server_name] = {
                    'proxies_service_list': [proxy],
                    'with_ssl': with_ssl,
                }
        for _, server_settings in servers.items():
            if not server_settings['proxies_service_list']:
                server_settings['proxies_service_list'] = [DEFAULT_PROXY_FOR_SERVER]

        if not servers:
            servers = {
                'default_server': {
                    'proxies_service_list': [DEFAULT_PROXY_FOR_SERVER],
                    'with_ssl': False,
                }
            }
        return servers

    def get_proxies(self) -> list:
        services_labels = self.parse_services_labeles()
        proxies_service_list = []
        for service_name, service in services_labels.items():
            domain = service.get('GATEWAY_INGRESS', {}).get('domain', {})
            domain_name = domain.get('name', "default_server")
            proxy_params = service.get('GATEWAY_INGRESS', {}).get('proxy', {})
            if proxy_params:
                for params in proxy_params.values():
                    custom_location_data = params.get('custom_location_data')
                    rewrites = params.get('rewrites')
                    if 'location' not in params or 'port' not in params:
                        continue
                    proxy = {
                        'location': params['location'],
                        'port': params['port'],
                        'service_name': service_name,
                        'custom_location_data': self._generate_custom_location_data(
                            custom_location_data
                        )
                        if custom_location_data
                        else [],
                        'rewrites': self._generate_rewrites(rewrites)
                        if rewrites
                        else [],
                        'rewrite_append_slash': (
                            params.get('rewrite_append_slash', '0') in TRUE_VALUES
                        ),
                        'proxy_pass_append_uri': (
                            params.get('proxy_pass_append_uri', '0') in TRUE_VALUES
                        ),
                        'proxy_set_header': (
                            params.get('proxy_set_header') or DEFAULT_PROXY_SET_HEADER
                        ),
                        'proxy_redirect': (
                            params.get('proxy_redirect') or DEFAULT_PROXY_REDIRECT
                        ),
                        'proxy_pass_request_headers': (
                            params.get('proxy_pass_request_headers')
                            or DEFAULT_PROXY_REQUEST_HEADER
                        ),
                        'domain_name': domain_name,
                    }
                    proxies_service_list.append(proxy)
        return proxies_service_list
