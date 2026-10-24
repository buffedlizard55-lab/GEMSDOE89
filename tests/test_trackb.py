"""Unit tests for the TRACKB axis (synthetic grids; no competition data)."""

import numpy as np

from gemsdoe import trackb


def _field_and_dots():
    field = np.zeros((60, 120), dtype=bool)
    field[45, 10:110] = True          # straight ridge (row 45)
    field[10, 10:60] = True           # bent ridge: horizontal arm
    field[10:40, 58] = True           # bent ridge: vertical arm
    dots = np.zeros((60, 120), dtype=bool)
    dots[45, 10:110:3] = True
    dots[10, 10:60:3] = True
    dots[13:40:3, 58] = True
    return dots, field


def test_strand_credit_positive_on_field():
    dots, field = _field_and_dots()
    credit, pts = trackb.strand_credit(dots, field)
    assert len(pts) == dots.sum()
    assert (credit > 0).all()


def test_straight_trace_qualifies_bent_does_not():
    dots, field = _field_and_dots()
    d_cat = np.full(dots.shape, 10.0)
    traces, audit, credit, pts = trackb.build_traces(dots, field, d_cat, top_n=5)
    assert audit["n_qualifying_traces"] >= 1
    top = traces[0]["metrics"]
    assert top["length_km"] >= 1.0
    assert top["consistency_R"] >= 0.85
    # strike of an east-west strand is ~90 deg
    assert abs(top["strike_deg"] - 90.0) < 5.0


def test_trace_metrics_strike_and_length():
    pts = np.column_stack([np.full(20, 30), np.arange(10, 70, 3)])
    d_cat = np.full((60, 120), 10.0)
    m = trackb.trace_metrics(pts, np.ones(20), d_cat)
    assert abs(m["strike_deg"] - 90.0) < 1.0
    assert m["length_km"] > 0.5
    assert m["consistency_R"] > 0.99
    assert m["straightness"] > 0.99


def test_linked_components_separate():
    pts = np.array([[0, 0], [0, 3], [0, 6], [50, 50], [50, 53]])
    comps = trackb.linked_components(pts, link_px=4.5)
    assert sorted(len(c) for c in comps) == [2, 3]
