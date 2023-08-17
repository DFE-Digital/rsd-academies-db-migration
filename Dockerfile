# This is deployed to fly.io

FROM nginx

COPY index.html /usr/share/nginx/html/
COPY nginx/default.conf.template /etc/nginx/conf.d/default.conf

RUN --mount=type=secret,id=nginx_auth \
    cat /run/secrets/nginx_auth > /etc/nginx/.htpasswd
