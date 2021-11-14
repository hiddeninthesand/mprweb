#!/bin/bash
set -eou pipefail

# Setup a config for our mysql db.
cp -vf "${CONFIG_FILE}" conf/config
sed -i "s;YOUR_AUR_ROOT;$(pwd);g" conf/config

python -m aurweb.initdb 2>/dev/null || /bin/true

exec "$@"
