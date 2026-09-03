# Johnson alpha-side P0 candidate receipt

Primary geometric input: Jesse Johnson, *Automorphisms of the three-torus
preserving a genus-three Heegaard splitting*, Pacific J. Math. 253 (2011),
75--94, arXiv:0708.2683.  Johnson's `alpha_ij` replaces the `x_i` square
diagonal by a path following `x_j` then `x_i`; the opposite push gives a
different splitting-preserving lift of the same transvection.

## Reproduction

```text
python3 scripts/factor_t73_matrix_johnson.py --check
python3 scripts/build_t73_johnson_lift.py --check
python3 scripts/search_t73_johnson_alpha_sides.py --check
python3 scripts/search_t73_johnson_alpha_sides.py --search --check
python3 scripts/generate_t73_johnson_alpha_movie.py --check
python3 scripts/straighten_t73_johnson_relative_ball.py --check
```

The matrix factorization has 93 unit `alpha_ij` moves.  The selected side
bits are:

```text
001001101010111011110000011011000001110110100101111101111101100001100101000110110110110100110
```

The deterministic search uses seed `730903`, 20 restarts and 300 bit flips
per restart.  On the recorded host it recovered a zero-score candidate in
approximately 32 seconds.

## Exact checks

```text
GAP_IS_BIJECTIVE=True
M2_LENGTH=311
M2_Y_PASSAGES=42
TOTAL_Y_CHANNELS=44
NET_RYZ_COEFFICIENT=0
EXACT_COMPACT_MATCH=True
```

This does not assert that all three compact straight words form a basis; GAP
proves that they do not.  The Johnson candidate uses different first and
third spine images while its reduced second image equals the compact `m2`
word exactly.

Every square in the 93-step spine movie is nondegenerate and has matching
endpoints.  Truncating in the moving unimodular basis gives basis-coordinate
clearance `1/4`.  The maximum inverse-basis infinity norm yields one uniform
physical protected-ball radius:

```text
1/196104
```

The subsequent collar and six-sweep generators complete this obligation.
Their hashes are assembled in `audit/t73_p0_johnson_certificate.json`; the
full certificate proves P0 for the explicit replacement presentation.
