FROM nginx:1.21.6-alpine

RUN apk add --update --no-cache \
    python3 \
    curl \
    cargo \
    bash \
    openssl \
    findutils \
    libffi \
    libffi-dev \
    libressl \
    libressl-dev \
    ncurses \
    procps \
    python3 \
    python3-dev \
    sed \
    && \
    ln -sf python3 /usr/bin/python

RUN python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools && \
    apk del \
    cargo \
    libffi-dev \
    libressl-dev \
    python3-dev \
    && \
    pip3 install docker-py jinja2 cffi certbot && \
    #Create new directories and set correct permissions.
    mkdir -p /var/www/letsencrypt && \
    rm -f /etc/nginx/conf.d/* && \ 
    chown 82:82 -R /var/www 
ENV DOCKER_HOST "unix:///var/run/docker.sock"
ENV UPDATE_INTERVAL "300"
ENV DEBUG "false"
ENV USE_REQUEST_ID "true"
ENV LOG_FORMAT "default"

ADD ./ingress /ingress
ADD ./docker-entrypoint.sh /docker-entrypoint.sh
ADD ./html/index.html /etc/nginx/html/index.html
ADD options-ssl-nginx.conf /etc/nginx/options-ssl-nginx.conf
ADD ssl-dhparams.pem /etc/nginx/ssl-dhparams.pem

HEALTHCHECK --interval=20s --timeout=2s --retries=2 \
    CMD curl -A " ~ GATEWAY health check ~" http://0.0.0.0 && kill -0 `cat /ingress/ingress.pid`

RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

WORKDIR /ingress/
CMD [ "python main.py" ]