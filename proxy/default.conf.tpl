server {
    # This will be set by our configuration
    listen ${LISTEN_PORT};

    # Serve files from /vol/static for requests matching /static path
    location /static {
        alias /vol/static;
    }

    # Catch-all location for other requests
    location / {
        # Pass requests to running uWSGI server via reverse proxy
        uwsgi_pass            ${APP_HOST}:${APP_PORT};

        # Include uWSGI parameters for request handling
        include               /etc/nginx/uwsgi_params;

        # Limit request body size to 10MB
        client_max_body_size 10M;
    }
}