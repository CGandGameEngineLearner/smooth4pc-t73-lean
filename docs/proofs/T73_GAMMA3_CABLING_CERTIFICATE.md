# Exact Gamma3 cabling certificate

**Status:** `DISCHARGED`

Run:

```text
python -B scripts/verify_t73_gamma3_magnus.py
python -I -B tests/test_t73_gamma3_magnus.py -v
```

## Artin--Magnus computation

Use the faithful Artin action of `B_44` on the free group `F_44`.  Expand the
image of every free generator in noncommuting Magnus variables and retain
degrees one, two and three.  The verifier processes all 11,340 Artin letters
with exact signed 64-bit integer arithmetic.  Every intermediate coefficient
has absolute value at most four, compared with the storage limit
`9223372036854775807`, so no modular or overflow inference is used.

For all 44 free generators the final linear part is the identity and every
quadratic and cubic coefficient is zero.  Equivalently, the Artin
automorphism is the identity on `F_44/Gamma_4(F_44)`.

## Lower central conclusion

Darn\'{e}, Theorem 6.2, proves the Andreadakis equality for the pure braid
group under the Artin action.  Therefore

\[
W\in\Gamma_3(P_{44}).
\]

Every physical cabling is a group homomorphism, so it carries
`Gamma_3(P_44)` into the third lower-central subgroup of the target pure
braid group.  Since every local pure braid generator is represented by
`I+O(h)`, commutator filtration gives

\[
\rho_h(W_s)-I\in h^3\operatorname{End}(E_s)
\]

for every oriented MWW cable state `s`.  This is the statewise divisibility
used by Theorem C.

Deleting one Artin letter changes the endpoint permutation and is rejected by
the mutation test.

