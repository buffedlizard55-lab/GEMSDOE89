#!/usr/bin/env python3
"""Mirror the root executive site into docs/ for either GitHub Pages source mode.

The root HTML is authoritative. Some older Pages settings use ``main/docs``;
others use ``main/root``. This generator keeps both entry points equivalent
without manually maintaining divergent HTML. It also copies only the two
research TIFs and their run cards needed by the docs-based deployment.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def render_docs_index(source: str) -> str:
    """Adjust root-site links for publication from the repository's docs folder."""
    return (source
            .replace('href="docs/HYPOTHESIS_REGISTER.md"', 'href="HYPOTHESIS_REGISTER.md"')
            .replace('href="docs/PROJECT_BRIEF.md"', 'href="PROJECT_BRIEF.md"')
            .replace('href="docs/legacy_fleet_20261024.html"', 'href="legacy_fleet_20261024.html"')
            .replace('href="releases/', 'href="downloads/'))


def render_docs_submit(source: str) -> str:
    """Adjust submission-guide links for publication from the docs folder."""
    return (source
            .replace('href="docs/HYPOTHESIS_REGISTER.md"', 'href="HYPOTHESIS_REGISTER.md"')
            .replace('href="releases/', 'href="downloads/'))


def mirror() -> None:
    # Retain the previously published fleet dashboard as an explicitly archived
    # page rather than silently discarding its historical content.
    old_index = DOCS / "index.html"
    archive = DOCS / "legacy_fleet_20261024.html"
    if old_index.exists() and not archive.exists():
        shutil.copy2(old_index, archive)
        old = archive.read_text()
        banner = (
            '<div style="border:3px solid #a00;background:#fee;padding:14px;margin:12px 0">'
            '<b>ARCHIVE — not current submission guidance.</b> Use the current '
            '<a href="index.html">executive summary</a> and its run cards; this '
            'snapshot predates later negative experiments and registry review.</div>\n'
        )
        archive.write_text(old.replace("<body>", "<body>\n" + banner, 1))

    # GitHub Pages configured to publish /docs serves this file at the site root.
    # Rebase paths to the docs publish root; generated copies below are explicit.
    index = render_docs_index((ROOT / "index.html").read_text())
    (DOCS / "index.html").write_text(index)

    submit = render_docs_submit((ROOT / "submit.html").read_text())
    (DOCS / "submit.html").write_text(submit)

    assets = DOCS / "downloads"
    assets.mkdir(parents=True, exist_ok=True)
    for name in (
        "h89-condedge-s2-4-20261024-829cc418-candidate.tif",
        "gems89-bstp40-20261024-2e7e8a8f-zeros.tif",
    ):
        shutil.copy2(ROOT / "releases" / name, assets / name)

    registry = DOCS / "registry"
    registry.mkdir(parents=True, exist_ok=True)
    for name in (
        "run_card_condedge_20261024.json",
        "run_card_bstp40.json",
        "submission_readiness.json",
    ):
        shutil.copy2(ROOT / "registry" / name, registry / name)
    (DOCS / ".nojekyll").touch()


def main() -> None:
    mirror()
    print("Mirrored root index.html and submit.html to docs/ Pages source with local assets.")


if __name__ == "__main__":
    main()
