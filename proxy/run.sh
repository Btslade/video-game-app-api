#!/bin/sh

set -e

# Substitutes environment variables defined in default.config.tpl
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

# Run server in the foreground to keep the container running
nginx -g 'daemon off;'
