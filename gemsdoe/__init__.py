"""GEMS Prize (DrivenData #306) candidate-raster toolkit.

Modules
  metric   -- DTI algebra, derived from the brief, unit-tested in tests/
  grid     -- the submission grid contract and byte-deterministic writing
  relief   -- the RELIEF axis (class definition, relocation, statistics)
  spacing  -- the SPACING axis (strike, Poisson-disk, hexagonal lattice)
  validate -- the hard gates
  proxy    -- REPORT-ONLY instruments (catalogue proxy, canary, SGMC, surrogate DTI)
"""

__all__ = ["metric", "grid", "relief", "spacing", "validate", "proxy"]
