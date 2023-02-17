import os
import time
import subprocess


def generate_letsencrypt_certs(domains: list) -> int:
    CERTBOT_EMAIL = os.environ['CERTBOT_EMAIL']
    for domain in domains:
        subprocess.call(
            [
                'certbot',
                'certonly',
                '--webroot',
                '--webroot-path=/var/www/letsencrypt',
                '-m',
                f'{CERTBOT_EMAIL}',
                '-d',
                f'{domain}',
                # '--standalone',
                '--agree-tos',
                '--keep',
                '-n',
            ]
        )
    livetime_cert = 30 * 86400
    renewal_timestamp = int(time.time() + livetime_cert)
    return renewal_timestamp
