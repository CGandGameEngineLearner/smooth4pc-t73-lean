# GAP free-basis and IA-search receipt

GAP was installed on the local Ubuntu/WSL host with:

```text
sudo -n apt-get install -y gap-core
```

APT installed GAP 4.12.1 and its packaged dependencies.  The proof-relevant
commands are:

```text
python3 scripts/check_t73_compact_free_basis.py --check --timeout 300
python3 scripts/search_t73_ia_representative.py --check --max-length 1
python3 scripts/construct_t73_ia_to_compact_movie.py --check
python3 scripts/search_t73_ia_framing.py --check --max-depth 3 --max-states 200000
```

The same GAP endomorphism test returned:

```text
GAP_VERSION=4.12.1
COMPACT:  IS_HOM=true IS_INJECTIVE=true IS_SURJECTIVE=false IS_BIJECTIVE=false
NIELSEN:  IS_HOM=true IS_INJECTIVE=true IS_SURJECTIVE=true  IS_BIJECTIVE=true
```

Thus the compact words of lengths 1, 310 and 1461 do not form a free basis of
`F_3`, while the explicit Nielsen positive control does.  The compact receipt
SHA-256 is:

```text
C3A02B0B5AFC7BFAA6DA0DDBDD48E629C6D5184FA0A35C64B12A6C22CCB39508
```

An inner correction by the conjugator `[-1]`, i.e. `x^-1`, is a GAP-certified
automorphism with unchanged abelianization, reduced `m2` length 311 and 44
total channels.  It is not the exact compact word.  The exact IA-to-compact
word movie has 11754 `r_yz` commutations and two free bigons; its net oriented
`r_yz` coefficient is `-40`.

The depth-three IA search visited 11869 distinct states and found 1768
channel-compatible candidates but no zero net coefficient; the best absolute
coefficient was 40.  This is a bounded negative search, not a proof that no
deeper IA correction exists.  A depth-four run capped at 50000 states was
truncated and likewise found no zero.

The dual-meridian extension search uses the same depth-three IA state set.
After excluding all basepoint-only corrections it finds 751 genuinely
detector-changing 44-channel candidates and zero candidates carrying the
three dual meridians to a signed permutation of their conjugacy classes.  The
latter is a sufficient but non-necessary extension condition.

The geometric audit subsequently checks that all three corrected images are
simultaneous conjugates and have the same cyclic classes as the original
Nielsen images.  Thus this correction is only a basepoint change in the same
outer automorphism class; its two additional word passages are not an
embedded 44-channel collar.

The Johnson-generator replacement resolves the algebraic obstruction without
using a common inner conjugation.  A 93-bit left/right square-diagonal choice
gives a GAP-certified free basis whose reduced `m2` word exactly equals the
compact 311-letter word, with 44 total channels and net `r_yz` coefficient
zero.  The deterministic search replay recovers the candidate in about 32
seconds on the recorded host.
