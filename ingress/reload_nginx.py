import subprocess


def reload_nginx():
    subprocess.call(['nginx', '-s', 'reload'])
