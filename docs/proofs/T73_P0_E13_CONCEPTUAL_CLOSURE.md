# Conceptual P0/E13 closure by Johnson mapping classes

Date: 2026-09-05

## Verdict

The proposed route is valid for constructing an unlabelled
Cappell--Shaneson handle decomposition and transporting its upper handles.
It does not identify the repository's fixed-marked detector tangle with the
11340-letter braid, and therefore does not prove the labelled P0 hypothesis
used by C.

The obstruction is relative boundary marking. A nontrivial pure braid cannot
be inserted into a fixed-endpoint tangle by an ambient isotopy fixed on the
boundary of the detector cylinder. If point-push is instead treated as an
ambient coordinate change, the endpoint modules, source vector and detector
row must all be transported. Naturality then conjugates the apparent braid
action, so the old fixed Burau evaluation cannot be retained.

## 1. Johnson mapping classes give a legitimate monodromy

Let the 93 signed side choices be the recorded word in Johnson's generators
alpha_ij. Each generator has an orientation-preserving representative of T3
preserving the genus-three Heegaard pair. Their composition gives a
splitting-preserving diffeomorphism psi whose induced map on H1 is the product
of the 93 elementary transvections, namely A.

Johnson's square move may be chosen to fix the common vertex q of the
coordinate spine. This point lies in the interior of one handlebody. Local
straightening changes psi by an isotopy supported in a small ball in that
handlebody and makes psi the identity on a smaller ball Bq. This does not
change its mapping class, action A, or preservation of the splitting.

This is an existence construction. It need not select the coordinate-level
ArmRestore stored by the repository.

## 2. Section framing

Because psi is the identity on Bq, the loop q times S1 in its mapping torus
has a product normal framing. An isotopy from the linear representative of A
to psi induces a mapping-torus diffeomorphism. Its normal derivative along
the traced section gives an element of pi1(SO(3)), and hence one of the two
Cappell--Shaneson framing parities.

The parity is not determined by A alone. It must be specified when the local
straightening is chosen. The two homotopy classes of oriented normal-frame
paths differ by the generator of pi1(SO(3)); choose the class transporting the
product framing to epsilon zero. Surgery on the section is then
diffeomorphic to Sigma_A^0.

A later point-push supported away from Bq has identity derivative near the
section and does not change epsilon.

## 3. AR handles, cancellations, and upper handles

Apply Aitchison--Rubinstein to psi and the preserved Heegaard pair. This gives
the embedded framed two-handles and their framing annuli. The section-surgery
handle and the mapping-torus one-handle form a product one/two pair. For the
chosen Johnson word, the first spine image has edge path z; after the first
cancellation the corresponding circle is z followed by x inverse and meets
the x belt sphere geometrically once. It is a second product one/two pair.

Standard handle calculus permits all other passages to be slid off before
each cancellation. This proves existence of a reduced handle presentation of
the same surgery manifold. It does not prove that the bands, lanes or
detector chart are the committed rational ones.

Transport every three-handle attaching sphere and the four-handle attaching
map through the boundary diffeomorphisms induced by the genuine slides and
cancellations. The transported upper handles complete Sigma_A^0. After the
boundary type is established, Laudenbach--Poenaru gives the equivalent
upper-handle uniqueness statement. No index-one/index-three cancellation is
used.

Thus this route gives a correct unlabelled E13 existence proof. It does not
identify the separately generated S sphere system or P3 cubical ball with the
transported upper handles.

## 4. Relative-boundary braid obstruction

Let T0 be 44 vertical arcs in D2 times I with endpoints and boundary disks
fixed. An ambient isotopy fixed on the full boundary is an isotopy of tangles
relative endpoints. Its image therefore represents the identity braid.

The public braid B44 is not the identity: its specialized Burau calculation
has divided cubic value 2624, whereas the identity matrix has zero such
coefficient. Hence no boundary-fixed ambient isotopy inserts B44 into T0.

A point-push is an isotopy h_t of the punctured disk with h_0 equal to the
identity and h_1 fixing the punctures. The mapping-cylinder map

    (x,t) maps to (h_t(x),t)

sends vertical strands to B44, but its top restriction is h_1 rather than the
identity of the marked punctured disk. It changes the endpoint marking.

There are two possible uses.

### Case A: ambient coordinate change of the complete presentation

Apply point-push to the complete framed link and upper handles, away from Bq.
The four-manifold and epsilon zero framing remain unchanged. But the outside
closure, endpoint identification, coefficient actions, source vector and
detector row are transported simultaneously. Functoriality gives conjugation.
The local B44 is accompanied by inverse endpoint or outside transport. One
cannot apply the old row and vector to B44 alone.

This preserves unlabelled P0/E13 but produces no new C value.

### Case B: genuine insertion relative to the fixed detector marking

Keep the outside link and endpoint parametrizations fixed and replace only
the vertical tangle by B44. Since B44 is nontrivial, this is not an ambient
isotopy relative to the ball boundary. It changes the framed attaching link
unless an additional sequence of genuine Kirby moves is proved. The
Sigma_A^0 and transported-upper-handle identification is therefore lost.

This permits the fixed Burau matrix to appear, but loses P0/E13.

There is no third option that both preserves the AR framed presentation and
retains B44 as an uncompensated operator on the old endpoint module.

## 5. The two r_xy passages

The selected channels consist of 42 m2 passages and two passages belonging to
the fiber dual-cell component r_xy. Postcomposing monodromy changes top images
of coordinate spine arcs, but does not by itself insert the same point-push
into r_xy. A common ambient diffeomorphism can move both types of passages,
but that is Case A and transports all marked data. Moving only the selected
pieces is Case B.

Thus postcomposing monodromy alone cannot realize the full committed
44-strand word with its fixed source binding.

## 6. Theorem

The 93 Johnson mapping classes, local straightening with chosen even normal
path, the AR construction, standard one/two cancellations, and transport of
the original upper handles produce a closed manifold diffeomorphic to
Sigma_A^0. Point-push away from the section preserves that diffeomorphism type
and framing parity when applied to the complete marked presentation.

However, these facts do not imply that the fixed-marked detector tangle is
B44 while its source and detector data remain unchanged. Boundary-fixed
insertion would force B44 to be braid-trivial; non-boundary-fixed point-push
transports the endpoint data and conjugates the categorical action.
Therefore this route closes only unlabelled P0/E13 existence, not the labelled
P0 required for C, S, or the value 2624.
