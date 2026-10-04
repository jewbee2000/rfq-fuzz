#!/bin/bash
set -euo pipefail
mkdir -p /home/consumer/setup-evidence /home/consumer/setup-inputs
exec > >(tee -a /home/consumer/setup-evidence/setup.log) 2>&1
set -x
date -u '+%Y-%m-%dT%H:%M:%SZ'
cat /etc/os-release
uname -a
python3 --version
curl --fail --silent --show-error http://10.0.2.2:28080/requirements-m0.lock -o /home/consumer/setup-inputs/requirements-m0.lock
curl --fail --silent --show-error http://10.0.2.2:28080/inspect_environment.py -o /home/consumer/setup-inputs/inspect_environment.py
curl --fail --silent --show-error http://10.0.2.2:28080/inspect_smoke.py -o /home/consumer/setup-inputs/inspect_smoke.py
curl --fail --silent --show-error http://10.0.2.2:28080/smoke.py -o /home/consumer/setup-inputs/smoke.py
sha256sum /home/consumer/setup-inputs/* > /home/consumer/setup-evidence/setup-input-hashes.txt
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3.12-venv poppler-utils libgl1 libglu1-mesa libxrender1 libxext6 libsm6 libglib2.0-0 fonts-dejavu-core
dpkg-query -W > /home/consumer/setup-evidence/system-packages.tsv
python3.12 -m venv /home/consumer/rfqfuzz-venv
/home/consumer/rfqfuzz-venv/bin/python -m pip install pip==26.2.1 --log /home/consumer/setup-evidence/pip-bootstrap.log
/home/consumer/rfqfuzz-venv/bin/python -m pip install -r /home/consumer/setup-inputs/requirements-m0.lock --report /home/consumer/setup-evidence/install-report.json --log /home/consumer/setup-evidence/pip-install.log
/home/consumer/rfqfuzz-venv/bin/python -m pip check
/home/consumer/rfqfuzz-venv/bin/python /home/consumer/setup-inputs/inspect_environment.py /home/consumer/setup-evidence/environment.json
mkdir -p /home/consumer/linux-smoke
cd /home/consumer/linux-smoke
/home/consumer/rfqfuzz-venv/bin/python /home/consumer/setup-inputs/smoke.py
/home/consumer/rfqfuzz-venv/bin/python /home/consumer/setup-inputs/inspect_smoke.py /home/consumer/linux-smoke/evidence/M0/smoke /home/consumer/setup-evidence/smoke-inspection.json
date -u '+%Y-%m-%dT%H:%M:%SZ'
touch /home/consumer/setup-evidence/SETUP_READY
echo RFQFUZZ_LINUX_VM_SETUP_READY
