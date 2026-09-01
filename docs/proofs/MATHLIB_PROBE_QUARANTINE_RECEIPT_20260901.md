# Mathlib probe quarantine receipt

At `2026-09-01T22:17:54+09:00`, 45 root-level untracked probe files were moved
out of the mathlib checkout used by the earlier R7 compile receipt.  They were
not deleted.

- source checkout: `D:/tmp/lean_joint_audit/mathlib4`
- source revision: `520045ab14e26149ee970e2e617ca04b09bde5d6`
- tracked modifications before the move: `0`
- moved entries: `45`, each previously reported by Git as `??`
- destination:
  `D:/tmp/smooth4pc_publish_mathlib_probe_quarantine_20260901T221754+0900`
- destination manifest: `QUARANTINE_MANIFEST.json`
- manifest SHA-256:
  `166C31BB011EE058141777F426616BB8E1694B8295ECF33CAFE55EDF9564E6C3`
- source checkout status after the move: empty

The quarantined files are older scaling-law `.lean`/`.olean` probes.  No
tracked mathlib source was edited.  The public release does not rely on this
checkout: its lockfile fetches the same revision into a new clone and the
release receipt rebuilds there.
