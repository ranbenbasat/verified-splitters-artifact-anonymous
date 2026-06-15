#!/usr/bin/env python3
"""Verify row files for (c,k,k)-splitters.

A row is a subset S of {0,...,c-1}, written as a binary string of length c.
The verifier checks that for every pair of disjoint k-sets A and B, some row
contains A and is disjoint from B.

With no file arguments, this script verifies every splitter_c*_k*_n*.rows.txt
file in the splitters/ directory. Pass one or more files to verify only those
files. The default verifier is self-contained Python; no external solver is
required.
"""

from __future__ import annotations

import argparse
import itertools
import re
import sys
import time
from collections import Counter, deque
from pathlib import Path


NAME_RE = re.compile(r"splitter_c(?P<c>\d+)_k(?P<k>\d+)_n(?P<n>\d+)\.rows\.txt$")


def parse_meta(path: Path) -> tuple[int, int, int]:
    match = NAME_RE.fullmatch(path.name)
    if not match:
        raise ValueError(
            f"{path.name}: expected filename splitter_cC_kK_nN.rows.txt"
        )
    return int(match.group("k")), int(match.group("c")), int(match.group("n"))


def read_rows(path: Path, c: int, expected_n: int) -> list[int]:
    masks: list[int] = []
    with path.open("r", encoding="ascii") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if len(line) != c or any(ch not in "01" for ch in line):
                raise ValueError(
                    f"{path.name}:{lineno}: expected a {c}-character 0/1 row"
                )
            mask = 0
            for i, ch in enumerate(line):
                if ch == "1":
                    mask |= 1 << i
            masks.append(mask)
    if len(masks) != expected_n:
        raise ValueError(f"{path.name}: filename says N={expected_n}, read {len(masks)}")
    if len(set(masks)) != len(masks):
        raise ValueError(f"{path.name}: duplicate rows detected")
    return masks


def popcount(mask: int) -> int:
    return bin(mask).count("1")


def row_histogram(masks: list[int]) -> str:
    hist = Counter(popcount(mask) for mask in masks)
    return " ".join(f"{size}:{hist[size]}" for size in sorted(hist))


def combinations_from_mask(mask: int, k: int) -> list[int]:
    bits = [i for i in range(mask.bit_length()) if (mask >> i) & 1]
    out: list[int] = []
    for combo in itertools.combinations(bits, k):
        m = 0
        for bit in combo:
            m |= 1 << bit
        out.append(m)
    return out


def mask_from_combo(combo: tuple[int, ...]) -> int:
    mask = 0
    for bit in combo:
        mask |= 1 << bit
    return mask


def positions(mask: int, n: int) -> list[int]:
    return [i for i in range(n) if (mask >> i) & 1]


def build_row_indexes(masks: list[int], c: int, k: int) -> tuple[dict[int, int], dict[int, int]]:
    all_colors = (1 << c) - 1
    contain: dict[int, int] = {}
    disjoint: dict[int, int] = {}
    for row_id, row in enumerate(masks):
        row_bit = 1 << row_id
        for combo in itertools.combinations(positions(row, c), k):
            am = mask_from_combo(combo)
            contain[am] = contain.get(am, 0) | row_bit
        for combo in itertools.combinations(positions(all_colors ^ row, c), k):
            bm = mask_from_combo(combo)
            disjoint[bm] = disjoint.get(bm, 0) | row_bit
    return contain, disjoint


def apply_perm(mask: int, perm: tuple[int, ...]) -> int:
    out = 0
    m = mask
    while m:
        lb = m & -m
        i = lb.bit_length() - 1
        out |= 1 << perm[i]
        m -= lb
    return out


def compose_perm(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[i]] for i in range(len(p)))


def perm_closure(gens: list[tuple[int, ...]], n: int) -> list[tuple[int, ...]]:
    ident = tuple(range(n))
    group = [ident]
    seen = {ident}
    queue = deque([ident])
    while queue:
        perm = queue.popleft()
        for gen in gens:
            nxt = compose_perm(gen, perm)
            if nxt not in seen:
                seen.add(nxt)
                group.append(nxt)
                queue.append(nxt)
    return group


def pair_reps_for_group(k: int, c: int, group: list[tuple[int, ...]]) -> list[tuple[int, int]]:
    k_masks = [mask_from_combo(combo) for combo in itertools.combinations(range(c), k)]
    seen_a: set[int] = set()
    areps: list[int] = []
    for am in k_masks:
        if am in seen_a:
            continue
        areps.append(am)
        for perm in group:
            seen_a.add(apply_perm(am, perm))

    reps: list[tuple[int, int]] = []
    for am in areps:
        stabilizer = [perm for perm in group if apply_perm(am, perm) == am]
        seen_b: set[int] = set()
        for bm in k_masks:
            if (am & bm) or bm in seen_b:
                continue
            reps.append((am, bm))
            for perm in stabilizer:
                seen_b.add(apply_perm(bm, perm))
    return reps


def verify_reps_with_indexes(
    masks: list[int], c: int, k: int, reps: list[tuple[int, int]], detail: str
) -> tuple[bool, str]:
    contain, disjoint = build_row_indexes(masks, c, k)
    for am, bm in reps:
        if (contain.get(am, 0) & disjoint.get(bm, 0)) == 0:
            return False, f"{detail} uncovered A={mask_to_set(am)} B={mask_to_set(bm)}"
    return True, f"{detail} checked={len(reps)}"


def psl2_19_group() -> list[tuple[int, ...]]:
    p = 19
    inf = p

    def add_one(x: int) -> int:
        return inf if x == inf else (x + 1) % p

    def neg_inv(x: int) -> int:
        if x == inf:
            return 0
        if x == 0:
            return inf
        return (-pow(x, -1, p)) % p

    return perm_closure(
        [
            tuple(add_one(x) for x in range(p + 1)),
            tuple(neg_inv(x) for x in range(p + 1)),
        ],
        p + 1,
    )


def psl3_4_on_21_group() -> list[tuple[int, ...]]:
    g1 = (3, 12, 17, 15, 6, 1, 0, 2, 4, 20, 9, 7, 14, 8, 10, 13, 19, 16, 11, 18, 5)
    g2 = (8, 20, 1, 12, 16, 6, 0, 5, 7, 4, 18, 15, 9, 13, 19, 10, 3, 11, 17, 2, 14)
    return perm_closure([g1, g2], 21)


def run_psl_group_verifier(
    masks: list[int], k: int, c: int, group: list[tuple[int, ...]], name: str
) -> tuple[bool, str]:
    if len(group[0]) != c:
        return False, f"{name}: group degree {len(group[0])} does not match c={c}"
    reps = pair_reps_for_group(k, c, group)
    return verify_reps_with_indexes(masks, c, k, reps, f"{name} reps={len(reps)}")


def run_k6_c22_psl_verifier(masks: list[int]) -> tuple[bool, str]:
    """Fast verifier for the PSL/H-symmetric k=6,c=22 constructions."""

    n_finite = 21
    extra_bit = 1 << 21
    finite_masks = {
        5: [mask_from_combo(combo) for combo in itertools.combinations(range(n_finite), 5)],
        6: [mask_from_combo(combo) for combo in itertools.combinations(range(n_finite), 6)],
    }

    def pair_reps(
        aw: int, bw: int, group: list[tuple[int, ...]]
    ) -> list[tuple[int, int]]:
        seen_a: set[int] = set()
        areps: list[int] = []
        for am in finite_masks[aw]:
            if am in seen_a:
                continue
            areps.append(am)
            for perm in group:
                seen_a.add(apply_perm(am, perm))

        reps: list[tuple[int, int]] = []
        for am in areps:
            stabilizer = [perm for perm in group if apply_perm(am, perm) == am]
            seen_b: set[int] = set()
            for bm in finite_masks[bw]:
                if (am & bm) or bm in seen_b:
                    continue
                reps.append((am, bm))
                for perm in stabilizer:
                    seen_b.add(apply_perm(bm, perm))
        return reps

    psl = psl3_4_on_21_group()
    base_line = sum(1 << i for i in range(5))
    h192 = [perm for perm in psl if perm[0] == 0 and apply_perm(base_line, perm) == base_line]
    if len(psl) != 20160 or len(h192) != 192:
        return False, f"k6,c22 special verifier group-size failure: {len(psl)}, {len(h192)}"

    contain, disjoint = build_row_indexes(masks, 22, 6)

    checked = 0
    cases = [
        ("66", pair_reps(6, 6, psl), lambda am: am, lambda bm: bm),
        ("65", pair_reps(6, 5, h192), lambda am: am, lambda bm: bm | extra_bit),
        ("56", pair_reps(5, 6, h192), lambda am: am | extra_bit, lambda bm: bm),
    ]
    for label, reps, wrap_a, wrap_b in cases:
        for am0, bm0 in reps:
            am, bm = wrap_a(am0), wrap_b(bm0)
            if (contain.get(am, 0) & disjoint.get(bm, 0)) == 0:
                return False, (
                    f"k6,c22 uncovered {label} A={mask_to_set(am)} "
                    f"B={mask_to_set(bm)}"
                )
            checked += 1
    return True, f"k6c22-psl-h checked={checked}"


def translate_mask(mask: int, shift: int, c: int) -> int:
    out = 0
    for i in range(c):
        if (mask >> i) & 1:
            out |= 1 << ((i + shift) % c)
    return out


def run_k6_c23_translation_verifier(masks: list[int]) -> tuple[bool, str]:
    """Fast verifier for translation-invariant k=6,c=23 constructions."""

    c = 23
    family = set(masks)
    for row in masks:
        if translate_mask(row, 1, c) not in family:
            return False, "k6,c23 special verifier expected translation invariance"

    contain, disjoint = build_row_indexes(masks, c, 6)
    all_color_mask = (1 << c) - 1
    seen_a: set[int] = set()
    reps_a: list[int] = []
    for combo in itertools.combinations(range(c), 6):
        am = mask_from_combo(combo)
        if am in seen_a:
            continue
        reps_a.append(am)
        for shift in range(c):
            seen_a.add(translate_mask(am, shift, c))

    checked = 0
    for am in reps_a:
        for bm in combinations_from_mask(all_color_mask ^ am, 6):
            if (contain.get(am, 0) & disjoint.get(bm, 0)) == 0:
                return False, (
                    f"k6,c23 uncovered A={mask_to_set(am)} B={mask_to_set(bm)}"
                )
            checked += 1
    return True, f"k6c23-translation A_reps={len(reps_a)} checked={checked}"


def run_python_verifier(
    masks: list[int], k: int, c: int, max_demands: int
) -> tuple[bool, str]:
    colors = range(c)
    all_color_mask = (1 << c) - 1
    ksets = []
    for combo in itertools.combinations(colors, k):
        m = 0
        for bit in combo:
            m |= 1 << bit
        ksets.append(m)

    total_demands = 0
    for am in ksets:
        total_demands += len(combinations_from_mask(all_color_mask ^ am, k))
    if max_demands and total_demands > max_demands:
        return (
            False,
            f"python fallback skipped: {total_demands} demands exceeds "
            f"--python-max-demands={max_demands}",
        )

    for am in ksets:
        containing_a = [w for w in masks if (am & ~w) == 0]
        for bm in combinations_from_mask(all_color_mask ^ am, k):
            if not any((bm & w) == 0 for w in containing_a):
                return False, f"uncovered A={mask_to_set(am)}, B={mask_to_set(bm)}"
    return True, "python"


def mask_to_set(mask: int) -> list[int]:
    return [i for i in range(mask.bit_length()) if (mask >> i) & 1]


def verify_file(path: Path, python_max_demands: int) -> bool:
    k, c, expected_n = parse_meta(path)
    masks = read_rows(path, c, expected_n)
    start = time.time()

    if c == 20 and k in (5, 6):
        ok, detail = run_psl_group_verifier(masks, k, c, psl2_19_group(), "psl2-19")
    elif k == 6 and c == 21:
        ok, detail = run_psl_group_verifier(masks, k, c, psl3_4_on_21_group(), "psl3-4")
    elif k == 6 and c == 22:
        ok, detail = run_k6_c22_psl_verifier(masks)
    elif k == 6 and c == 23:
        ok, detail = run_k6_c23_translation_verifier(masks)
    else:
        ok, detail = run_python_verifier(masks, k, c, python_max_demands)

    elapsed = time.time() - start
    status = "OK" if ok else "FAIL"
    print(
        f"{status} {path.name} k={k} c={c} N={len(masks)} "
        f"hist={row_histogram(masks)} method={detail if ok else 'none'} "
        f"time={elapsed:.2f}s"
    )
    if not ok:
        print(detail, file=sys.stderr)
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="specific .rows.txt files to verify")
    parser.add_argument(
        "--python-max-demands",
        type=int,
        default=0,
        help="maximum demands allowed for the pure-Python fallback",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    paths = [Path(file).resolve() for file in args.files]
    if not paths:
        paths = sorted((script_dir / "splitters").glob("splitter_c*_k*_n*.rows.txt"))
        if not paths:
            paths = sorted(script_dir.glob("splitter_c*_k*_n*.rows.txt"))
    if not paths:
        print("No splitter row files found.", file=sys.stderr)
        return 2

    all_ok = True
    for path in paths:
        all_ok = verify_file(path, args.python_max_demands) and all_ok
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
