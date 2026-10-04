#!/bin/bash
set -euo pipefail
set -x
exec > /home/consumer/setup-evidence/bounded-install.log 2>&1
unset PYTHONPATH
cd /home/consumer
curl --fail --silent --show-error http://127.0.0.1:28080/frozen-consumer-bounded.tar.gz -o frozen-consumer-bounded.tar.gz
echo 'e859283037daac28e2664b3939ed3846a3b602d511610f0d6362705436719931  frozen-consumer-bounded.tar.gz' | sha256sum -c -
mkdir frozen-bounded
tar -xf frozen-consumer-bounded.tar.gz -C frozen-bounded
cd frozen-bounded
/home/consumer/rfqfuzz-venv/bin/python -m pip install --no-index -r requirements-v1.lock -r requirements-build.lock --report /home/consumer/setup-evidence/bounded-dependencies-report.json --log /home/consumer/setup-evidence/bounded-dependencies-pip.log
/home/consumer/rfqfuzz-venv/bin/python -m pip install --no-index --no-deps --no-build-isolation -e . --report /home/consumer/setup-evidence/bounded-project-report.json --log /home/consumer/setup-evidence/bounded-project-pip.log
/home/consumer/rfqfuzz-venv/bin/python -m pip check
/home/consumer/rfqfuzz-venv/bin/python -m rfqfuzz.v1 demo --help
sha256sum /home/consumer/frozen-consumer-bounded.tar.gz /home/consumer/frozen-bounded/requirements*.lock > /home/consumer/setup-evidence/bounded-input-hashes.txt
date -u +%Y-%m-%dT%H:%M:%SZ
touch /home/consumer/setup-evidence/BOUNDED_INSTALL_READY
