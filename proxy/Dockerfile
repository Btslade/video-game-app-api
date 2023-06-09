# Image will use non-root user for improved security
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="Braeden"

# Copy files to image
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

# Set environment variables
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

# Switch to root user to perform setup tasks
USER root

# Create directory for static files and set permissions
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static

# Create an empty default.conf and set ownership and permissions for Nginx user
RUN touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf

# Make run.sh executable
RUN chmod +x /run.sh

# Store static data
VOLUME /vol/static

# Switch to nginx user
USER nginx

# Execute the run script
CMD ["/run.sh"]
