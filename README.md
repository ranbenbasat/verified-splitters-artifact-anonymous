# Verified (c,k,k)-splitter rows

This repository contains explicit row families for several `(c,k,k)`-splitters.
A family `F` of subsets of `{0,...,c-1}` is treated as a `(c,k,k)`-splitter if
for every pair of disjoint sets `A,B` with `|A|=|B|=k`, there is a row `S in F`
such that `A subset S` and `S cap B = emptyset`.

The repository is application-neutral: it records the splitter instances, a
self-contained verifier, and the raw exponent values associated with the listed
row counts. It does not rely on any external project checkout or compiled
solver.

## Contents

- `splitters/*.rows.txt`: human-readable row files. Each nonblank line is a
  binary string of length `c`; position `i` is `1` exactly when color `i` is in
  that row.
- `manifest.tsv`: file names, parameters, row-size histograms, and SHA-256
  hashes.
- `results_raw.tsv`: raw exponents before any composition operation.
- `verify_splitters.py`: exact verifier for all listed rows.
- `tex/splitter_artifact_section.tex`: a LaTeX section describing the artifact
  and the raw exponent table.

## Verification

Verify everything:

```bash
python verify_splitters.py
```

Verify one file:

```bash
python verify_splitters.py splitters/splitter_c14_k4_n407.rows.txt
```

The verifier is exact. For smaller instances it checks all demands directly;
for the largest symmetric instances it uses explicit group actions to reduce to
orbit representatives and then checks the same containment/disjointness
condition.

## Raw exponent table

The column `2^E` is the raw base before compositions.

| c | k | rows | E | 2^E |
|---:|---:|---:|---:|---:|
| 11 | 3 | 66 | 1.972683226820 | 3.924974352460 |
| 12 | 3 | 98 | 2.003465764389 | 4.009620690451 |
| 13 | 3 | 112 | 2.013680782179 | 4.038111599039 |
| 11 | 4 | 262 | 1.998548968447 | 3.995978908782 |
| 12 | 4 | 307 | 1.988961937364 | 3.969512769671 |
| 13 | 4 | 377 | 1.988793020251 | 3.969048028776 |
| 14 | 4 | 407 | 1.985754104495 | 3.960696362076 |
| 15 | 4 | 415 | 1.983972235511 | 3.955807535761 |
| 16 | 4 | 576 | 2.001043703590 | 4.002894807787 |
| 15 | 5 | 1933 | 1.996642526902 | 3.990701931489 |
| 16 | 5 | 1933 | 1.986911942179 | 3.963876302433 |
| 17 | 5 | 2618 | 1.993778871392 | 3.982788504994 |
| 18 | 5 | 2856 | 1.994396115148 | 3.984492868863 |
| 19 | 5 | 3338 | 2.000011064766 | 4.000030678163 |
| 20 | 5 | 3382 | 2.002473116746 | 4.006862816154 |
| 19 | 6 | 10402 | 1.988010819194 | 3.966896671764 |
| 20 | 6 | 10754 | 1.985521558077 | 3.960057993262 |
| 21 | 6 | 11930 | 1.987349907432 | 3.965079816394 |
| 22 | 6 | 14175 | 1.992409316705 | 3.979009426067 |
| 23 | 6 | 21068 | 2.003539178137 | 4.009824731335 |

## Notes

The files intentionally avoid application-specific framing. They are simply
certificates of the listed `(c,k,k)` splitter families.
