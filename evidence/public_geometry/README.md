# Public geometry evidence

These are the exact files previously cited from machine-local `D:/tmp` paths
by the proof documents.  They are copied byte-for-byte; `SHA256SUMS` records
their frozen identities.

The bundle closes the immediate review gap: a GitHub clone now contains the
actual E1 cable certificate, G1 presentation/cut/framing/PD inputs, and all
three E8 chosen-sphere certificates rather than only their hashes and six
reported scalar zeros.

Run from the repository root:

```text
python -I -B scripts/verify_public_geometry_evidence.py
```

The verifier checks every byte hash, parses every JSON object, recomputes the
2,126,291-crossing global-descending certificate from the bundled PD, and
checks the stored chosen-sphere schemas, determinant and scalar fields.  It
does not regenerate the three chosen-sphere certificates from their upstream
hundreds-of-megabytes construction trees; those certificates remain objects
for independent mathematical inspection, not Lean theorems.
