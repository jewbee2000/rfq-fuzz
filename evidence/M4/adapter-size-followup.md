# Adapter resource-bound follow-up

After T12 closure, coordinator review identified two useful hardening changes:
oversized manual input now retains a structured rejection before copying/parsing,
and local adapter stdout/stderr spool to files with monitored output limits rather
than accumulating in memory. Exceeded limits kill the process tree and preserve
the reason and logs. Original oversized inputs remain at their supplied source.

Actual command: `./.venv/Scripts/python.exe -m pytest tests/adapters tests/reporting -q`.
Result **8 passed in 3.54 s**, including actual oversized input and live output-limit
termination controls. Output: `evidence/M4/adapter-size-followup.txt`. These are
supplemental R12/R19 checks, not a broader claim of a security sandbox.
