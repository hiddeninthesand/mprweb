#!/bin/bash
set -eou pipefail

# Setup a config for our mysql db.
cp -vf "${CONFIG_FILE}" conf/config
sed -i "s;YOUR_AUR_ROOT;$(pwd);g" conf/config
sed -ri "s;^(aur_location) = .+;\1 = ${AURWEB_FASTAPI_PREFIX:-'http://127.0.0.1:8080'};" conf/config

# Setup Redis for FastAPI.
sed -ri 's/^(cache) = .+/\1 = redis/' conf/config
sed -ri 's|^(redis_address) = .+|\1 = redis://redis|' conf/config

if [ ! -z ${COMMIT_HASH+x} ]; then
    sed -ri "s/^;?(commit_hash) =.*$/\1 = $COMMIT_HASH/" conf/config
fi

sed -ri "s|^(git_clone_uri_anon) = .+|\1 = ${AURWEB_FASTAPI_PREFIX}/%s.git|" conf/config.defaults
sed -ri "s|^(git_clone_uri_priv) = .+|\1 = ${AURWEB_SSHD_PREFIX}/%s.git|" conf/config.defaults

rm -rf $PROMETHEUS_MULTIPROC_DIR
mkdir -p $PROMETHEUS_MULTIPROC_DIR

exec "$@"
