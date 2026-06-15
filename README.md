# Verified (c,k,k)-splitter rows

This repository contains explicit row families for several `(c,k,k)`-splitters.
A family `F` of subsets of `{0,...,c-1}` is treated as a `(c,k,k)`-splitter if
for every pair of disjoint sets `A,B` with `|A|=|B|=k`, there is a row `S in F`
such that `A subset S` and `S cap B = emptyset`.

The repository is application-neutral: it records the splitter instances and a
self-contained verifier. It does not rely on any external project checkout or
compiled solver.

## Contents

- `splitters/*.rows.txt`: human-readable row files. Each nonblank line is a
  binary string of length `c`; position `i` is `1` exactly when color `i` is in
  that row.
- `manifest.tsv`: file names, parameters, row-size histograms, and SHA-256
  hashes.
- `verify_splitters.py`: exact verifier for all listed rows.

## Splitter sizes

| k | c | rows | file |
|---:|---:|---:|---|
| 3 | 11 | 66 | `splitters/splitter_c11_k3_n66.rows.txt` |
| 3 | 12 | 98 | `splitters/splitter_c12_k3_n98.rows.txt` |
| 3 | 13 | 112 | `splitters/splitter_c13_k3_n112.rows.txt` |
| 4 | 11 | 262 | `splitters/splitter_c11_k4_n262.rows.txt` |
| 4 | 12 | 307 | `splitters/splitter_c12_k4_n307.rows.txt` |
| 4 | 13 | 377 | `splitters/splitter_c13_k4_n377.rows.txt` |
| 4 | 14 | 407 | `splitters/splitter_c14_k4_n407.rows.txt` |
| 4 | 15 | 415 | `splitters/splitter_c15_k4_n415.rows.txt` |
| 4 | 16 | 576 | `splitters/splitter_c16_k4_n576.rows.txt` |
| 5 | 15 | 1933 | `splitters/splitter_c15_k5_n1933.rows.txt` |
| 5 | 16 | 1933 | `splitters/splitter_c16_k5_n1933.rows.txt` |
| 5 | 17 | 2618 | `splitters/splitter_c17_k5_n2618.rows.txt` |
| 5 | 18 | 2856 | `splitters/splitter_c18_k5_n2856.rows.txt` |
| 5 | 19 | 3338 | `splitters/splitter_c19_k5_n3338.rows.txt` |
| 5 | 20 | 3382 | `splitters/splitter_c20_k5_n3382.rows.txt` |
| 6 | 19 | 10402 | `splitters/splitter_c19_k6_n10402.rows.txt` |
| 6 | 20 | 10754 | `splitters/splitter_c20_k6_n10754.rows.txt` |
| 6 | 21 | 11930 | `splitters/splitter_c21_k6_n11930.rows.txt` |
| 6 | 22 | 14175 | `splitters/splitter_c22_k6_n14175.rows.txt` |
| 6 | 23 | 21068 | `splitters/splitter_c23_k6_n21068.rows.txt` |

## Ownership commitment

SHA-256 commitment: `68edc42dda15df9db330c85e1fa2c5c478ceb397f344f1ee90143d39f9cf4b69`.

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

## Notes

The files intentionally avoid application-specific framing. They are simply
certificates of the listed `(c,k,k)` splitter families.
