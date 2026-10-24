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


def test_static_pages_have_no_broken_local_links_and_warn_on_submission():
    for filename in ("index.html", "submit.html"):
        text = (ROOT / filename).read_text()
        parser = Links()
        parser.feed(text)
        assert "DO NOT SUBMIT" in text
        assert "HOLDOUT-DTI" in text
        for href in parser.hrefs:
            parsed = urlparse(href)
            if parsed.scheme or href.startswith("#"):
                continue
            target = (ROOT / parsed.path).resolve()
            assert target.exists(), f"broken local link in {filename}: {href}"
