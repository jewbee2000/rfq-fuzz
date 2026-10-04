#!/bin/bash
set -euo pipefail
set -x
exec > /home/consumer/linux-family-semantic-launch.log 2>&1
mkdir /home/consumer/linux-semantic-inspection
/home/consumer/rfqfuzz-venv/bin/python /home/consumer/measure_public_review.py /home/consumer/linux-bounded-workflow/generated-suite/public/pk-780fa2354eea /home/consumer/linux-semantic-inspection/plate > /home/consumer/linux-semantic-inspection/plate.log 2>&1
/home/consumer/rfqfuzz-venv/bin/python /home/consumer/measure_public_review.py /home/consumer/linux-bounded-workflow/generated-suite/public/pk-c02891e82f64 /home/consumer/linux-semantic-inspection/bore_block > /home/consumer/linux-semantic-inspection/bore_block.log 2>&1
/home/consumer/rfqfuzz-venv/bin/python /home/consumer/measure_public_review.py /home/consumer/linux-bounded-workflow/generated-suite/public/pk-d66a90fd926a /home/consumer/linux-semantic-inspection/pocket_block > /home/consumer/linux-semantic-inspection/pocket_block.log 2>&1
/home/consumer/rfqfuzz-venv/bin/python /home/consumer/check_family_semantics.py /home/consumer/linux-semantic-inspection > /home/consumer/linux-semantic-inspection/summary.log 2>&1
touch /home/consumer/linux-semantic-inspection/SEMANTICS_READY
