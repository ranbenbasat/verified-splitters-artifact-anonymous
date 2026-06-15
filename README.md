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
