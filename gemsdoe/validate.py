"""Hard gates for a candidate release raster.

Every gate here is binary and must pass before a file is offered to the human.
Report-only measurements (catalogue proxy, canary) live in proxy.py and are
never able to fail a file.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .grid import sha256_file


def _contract_equal(a, b, keys=("shape", "dtype", "pixel_scale", "tiepoint", "geokeys")):
    diffs = {}
    for k in keys:
        if a.get(k) != b.get(k):
            diffs[k] = {"got": a.get(k), "want": b.get(k)}
    return diffs


def gate_release(path, contract, footprint=None, dots_mask=None,
                 require_nan_outside=None, ledger_hashes=(), min_clearance_px=0.0,
                 clearance_raster=None):
    """Run the MUST gates. Returns (ok, list_of_results).

    footprint / dots_mask / clearance_raster are optional so the same gate
    function works in CI, where the competition rasters are not present: the
    grid contract is compared against the committed registry/grid_contract.json
    and the value-domain checks are run on the release alone.
    """
    from .grid import read_contract_from_tiff

    results = []

    def add(name, ok, detail=""):
        results.append({"gate": name, "ok": bool(ok), "detail": detail})

    path = Path(path)
    arr = None
    try:
        import tifffile

        arr = tifffile.imread(path)
        ok = True
    except Exception as exc:  # noqa: BLE001
        ok = False
        add("readable", False, repr(exc))
        return False, results
    if arr is not None:
        add("readable", True, f"{path.name}")

    try:
        got = read_contract_from_tiff(path)
    except Exception as exc:
        add("grid_contract", False, repr(exc))
        return False, results
    for name, mask in (("footprint", footprint), ("dots_mask", dots_mask),
                       ("clearance_raster", clearance_raster)):
        if mask is not None and np.asarray(mask).shape != arr.shape:
            add("mask_shape", False, f"{name} shape differs from raster")
            return False, results
    diffs = _contract_equal(got, contract)
    add("grid_contract", not diffs, json.dumps(diffs) if diffs else "matches template")

    add("dtype_float32", str(arr.dtype) == "float32", str(arr.dtype))
    add("single_band", arr.ndim == 2, f"ndim={arr.ndim}")
    add("shape", list(arr.shape) == list(contract["shape"]), str(list(arr.shape)))
    add("crs_epsg32611", got.get("geographic_crs") == "EPSG:32611", got.get("geographic_crs"))

    add("no_infinity", not np.isinf(arr).any(), "infinity is never valid nodata")
    finite = np.isfinite(arr)
    inside = arr[finite]
    in_range = bool(inside.size == 0 or ((inside >= 0) & (inside <= 1)).all())
    bad = int(((inside < 0) | (inside > 1)).sum()) if inside.size else 0
    add("values_in_0_1", in_range, f"{bad} out-of-range px; min={inside.min() if inside.size else None}, max={inside.max() if inside.size else None}")

    if require_nan_outside is False:
        n_nan = int((~finite).sum())
        add("no_nan_anywhere", n_nan == 0, f"{n_nan} NaN px")

    if footprint is not None:
        inside_nan = int((~finite & footprint).sum())
        add("no_nan_inside_footprint", inside_nan == 0, f"{inside_nan} NaN px inside")
        if require_nan_outside is True:
            outside_finite = int((~np.isnan(arr) & ~footprint).sum())
            add("nan_outside_footprint", outside_finite == 0, f"{outside_finite} finite px outside")
        elif require_nan_outside is False:
            outside_zero = bool(np.all(arr[~footprint] == 0))
            add("zeros_outside_footprint", outside_zero, "0 outside")

    if dots_mask is not None:
        n_dots = int(dots_mask.sum())
        add("unit_dots", bool(np.all(arr[dots_mask] == 1.0)), f"{n_dots} dots all == 1.0")
        add("dot_count_matches_mask", int((finite & (arr > 0)).sum()) == n_dots,
            f"raster {(finite & (arr > 0)).sum()} vs mask {n_dots}")

    if clearance_raster is not None and dots_mask is not None:
        cat = clearance_raster > 0
        n_on = int((dots_mask & cat).sum())
        add("zero_catalogue_mass", n_on == 0, f"{n_on} dots on catalogue pixels")
        if min_clearance_px > 0:
            from scipy import ndimage as ndi

            d = ndi.distance_transform_edt(~cat)[dots_mask]
            n_close = int((d < min_clearance_px).sum())
            add("catalogue_clearance", n_close == 0,
                f"{n_close} dots closer than {min_clearance_px} px; min={d.min() if d.size else None}")

    sha = sha256_file(path)
    add("sha256_not_in_ledger", sha not in set(ledger_hashes), sha[:16])

    ok = all(r["ok"] for r in results)
    return ok, results
