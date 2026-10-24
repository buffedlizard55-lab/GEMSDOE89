"""GEMS Prize (DrivenData #306) candidate-raster toolkit.

Modules
  metric   -- DTI algebra, derived from the brief, unit-tested in tests/
  grid     -- the submission grid contract and byte-deterministic writing
  relief   -- the RELIEF axis (class definition, relocation, statistics)
  trackb   -- the TRACKB axis (Phase-2 strike-consistent traces)
  validate -- the hard gates
  proxy    -- REPORT-ONLY instruments (catalogue proxy, canary, surrogate DTI)
"""

__all__ = ["metric", "grid", "relief", "validate", "proxy", "trackb"]
