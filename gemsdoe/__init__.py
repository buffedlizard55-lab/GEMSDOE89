"""GEMS Prize (DrivenData #306) candidate-raster toolkit.

Modules
  metric   -- DTI algebra, derived from the brief, unit-tested in tests/
  grid     -- the submission grid contract and byte-deterministic writing
  relief   -- the RELIEF axis (class definition, relocation, statistics)
  trackb   -- the TRACKB axis (Phase-2 top12 strike-consistent trace overlay, PR #15)
  trackb_conc -- the TRACKB-conc axis (Phase-2 inventory + count-preserving
                 structural concentration, TR10/TR20/TR30)
  validate -- the hard gates
  proxy    -- REPORT-ONLY instruments (catalogue proxy, canary, surrogate DTI)
"""

__all__ = ["metric", "grid", "relief", "validate", "proxy", "trackb", "trackb_conc"]
