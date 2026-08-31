# Locked Lake evidence

This directory preserves the remote wrapper run with its original relative
paths. `LOCKED_LAKE_RUN_MANIFEST.sha256` remains at the archive root;
`scripts/locked_lake.sh` and every `logs/...` entry occupy the paths written in
that manifest. No flattened duplicate is retained.

Direct replay from this directory:

```sh
sha256sum -c LOCKED_LAKE_RUN_MANIFEST.sha256
```

The captured standard output is `DIRECT_SHA256_REPLAY.log`. It contains seven
`OK` rows, zero mismatches, and has SHA-256
`AE7BFBE60C319A827D601A2463D6474D9139BCB84C7C0F93782B48E89E4A9E1A`.

This is a local evidence-layout repair only. It did not modify the remote
sandbox and did not rerun Lake or Lean.
