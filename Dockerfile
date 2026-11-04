# syntax=docker/dockerfile:1
FROM php:8.3-cli-bookworm
RUN --mount=type=secret,id=proxy_ca,required=true \
    apt-get -o Acquire::https::CaInfo=/run/secrets/proxy_ca update && \
    apt-get -o Acquire::https::CaInfo=/run/secrets/proxy_ca install -y --no-install-recommends libonig-dev && \
    docker-php-ext-install -j2 pdo_mysql mbstring && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --chown=www-data:www-data . /app
RUN mkdir -p /app/storage && chown -R www-data:www-data /app/storage
USER www-data
EXPOSE 8080
CMD ["php","-S","0.0.0.0:8080","-t","public","public/router.php"]
