#!/bin/bash
set -eou pipefail

for archive in packages pkgbase users packages-meta-v1.json packages-meta-ext-v1.json; do
    ln -vsf /var/lib/aurweb/archives/${archive}.gz /aurweb/web/html/${archive}.gz
done

# Setup a config for our mysql db.
cp -vf conf/config.dev conf/config
sed -i "s;YOUR_AUR_ROOT;$(pwd);g" conf/config
sed -ri "s;^(aur_location) = .+;\1 = ${AURWEB_FASTAPI_PREFIX:-'http://127.0.0.1:8080'};" conf/config

items=('DB_USER/user' 'DB_PASSWORD/password' 'SMTP_SERVER/smtp-server' 'SMTP_PORT/smtp-port'
       'SMTP_USE_SSL/smtp-use-ssl' 'SMTP_USE_STARTTLS/smtp-use-starttls' 'SMTP_USER/smtp-user'
       'SMTP_PASSWORD/smtp-password' 'SMTP_SENDER/sender' 'SMTP_REPLY_TO/reply-to')

for i in "${items[@]}"; do
    IFS="/" read -r var config_item < <(echo "${i}")

    if [[ "${!var:+x}" == "x" ]]; then
        sed -i "s;^${config_item} =.*;${config_item} = ${!var};" conf/config
    fi
done

if [[ "${SESSION_SECRET:+x}" == "" ]]; then
    SESSION_SECRET="$(openssl rand -hex 20)"
fi

sed -i "s;session_secret = secret;session_secret = ${SESSION_SECRET};" conf/config

# Enable memcached.
sed -ri 's/^(cache) = .+$/\1 = memcache/' conf/config

sed -ri "s|^(git_clone_uri_anon) = .+|\1 = ${AURWEB_PHP_PREFIX}/%s.git|" conf/config.defaults
sed -ri "s|^(git_clone_uri_priv) = .+|\1 = ${AURWEB_SSHD_PREFIX}/%s.git|" conf/config.defaults

sed -ri 's/^(listen).*/\1 = 0.0.0.0:9000/' /etc/php/php-fpm.d/www.conf
sed -ri 's/^;?(clear_env).*/\1 = no/' /etc/php/php-fpm.d/www.conf

# Log to stderr. View logs via `docker-compose logs php-fpm`.
sed -ri 's|^(error_log) = .*$|\1 = /proc/self/fd/2|g' /etc/php/php-fpm.conf
sed -ri 's|^;?(access\.log) = .*$|\1 = /proc/self/fd/2|g' \
    /etc/php/php-fpm.d/www.conf

sed -ri 's/^;?(extension=pdo_mysql)/\1/' /etc/php/php.ini
sed -ri 's/^;?(open_basedir).*$/\1 = \//' /etc/php/php.ini

# Use the sqlite3 extension line for memcached.
sed -ri 's/^;(extension)=sqlite3$/\1=memcached/' /etc/php/php.ini

exec "$@"
