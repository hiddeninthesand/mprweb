#!/bin/bash
set -eou pipefail
dir=$(dirname $0)


# Clean up coverage and stuff.
make -C test clean

# Set up config file.
cp "${CONFIG_FILE}" conf/config
sed -i 's|^password =.*|;&|' conf/config
sed -i 's|^user =.*|user = root|' conf/config
sed -i 's|^port =.^|;&|' conf/config
sed -i "s|YOUR_AUR_ROOT|$(pwd)|" conf/config

# Run sharness tests.
bash $dir/run-sharness.sh

# Pytest also sets up the config file, so we'll remove the one we set up.
rm conf/config

# Run Python tests with MariaDB database.
# Pass --silence to avoid reporting coverage. We will do that below.
bash $dir/run-pytests.sh --no-coverage

make -C test coverage

# /data is mounted as a volume. Copy coverage into it.
# Users can then sanitize the coverage locally in their
# aurweb root directory: ./util/fix-coverage ./data/.coverage
rm -f /data/.coverage
cp -v .coverage /data/.coverage
chmod 666 /data/.coverage

# Run flake8 and isort checks.
for dir in aurweb test migrations; do
    flake8 --count $dir
    isort --check-only $dir
done
