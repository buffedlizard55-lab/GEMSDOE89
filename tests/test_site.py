from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        self.hrefs.extend(value for key, value in attrs if key == "href" and value)


def _check_links(base: Path, filename: str, text: str):
    parser = Links()
    parser.feed(text)
    assert "DO NOT SUBMIT" in text
    assert "HOLDOUT-DTI" in text
    for href in parser.hrefs:
        parsed = urlparse(href)
        if parsed.scheme or href.startswith("#"):
            continue
        target = (base / parsed.path).resolve()
        assert target.exists(), f"broken local link in {filename}: {href}"


def test_static_pages_have_no_broken_local_links_and_warn_on_submission():
    for filename in ("index.html", "submit.html"):
        text = (ROOT / filename).read_text()
        _check_links(ROOT, filename, text)


def test_docs_pages_mirror_root_site_and_ship_download_assets():
    from tools.build_pages_site import render_docs_index, render_docs_submit

    root_index = (ROOT / "index.html").read_text()
    root_submit = (ROOT / "submit.html").read_text()
    docs_index = (ROOT / "docs" / "index.html").read_text()
    docs_submit = (ROOT / "docs" / "submit.html").read_text()
    assert docs_index == render_docs_index(root_index)
    assert docs_submit == render_docs_submit(root_submit)
    _check_links(ROOT / "docs", "docs/index.html", docs_index)
    _check_links(ROOT / "docs", "docs/submit.html", docs_submit)
    assert (ROOT / "docs" / "downloads" / "h89-condedge-s2-4-20261024-829cc418-candidate.tif").exists()
    assert (ROOT / "docs" / "registry" / "run_card_condedge_20261024.json").exists()
    assert (ROOT / "docs" / "registry" / "run_card_bstp40.json").exists()
    assert (ROOT / "docs" / ".nojekyll").exists()
