"""Validate local URLs in the exported HTML and CSS before publishing."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        # Connection hints point to an origin, not to a page or file.
        # Next.js emits <link rel="preconnect" href="/"> on static pages.
        if tag == "link" and dict(attrs).get("rel", "").lower() in (
            "preconnect", "dns-prefetch"
        ):
            return
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.urls.append(value)


def check(root, base):
    errors = set()
    pages = list(root.rglob("*.html"))
    if not (root / "index.html").is_file():
        errors.add("Missing index.html")
    for course in ("dagster-essentials", "dagster-etl", "dagster-dbt",
                   "dagster-testing", "ai-driven-data-engineering"):
        if not (root / course / "index.html").is_file():
            errors.add(f"Missing course: {course}")

    def check_url(file, value):
        parsed = urlsplit(value)
        # Keep external docs and untranslated material external. A course link
        # with a local exported equivalent must stay on the translated site.
        original_route = None
        if parsed.hostname == "courses.dagster.io" and parsed.path.startswith("/courses/"):
            original_route = parsed.path.removeprefix("/courses/")
        elif parsed.hostname == "dagster-university.dagster-docs.io":
            original_route = parsed.path.lstrip("/")
        if original_route is not None:
            relative_route = unquote(original_route).rstrip("/")
            # Only treat safe, actual exported pages as translated equivalents.
            if ".." not in Path(relative_route).parts and not relative_route.startswith("/"):
                local_page = root / relative_route
                if (local_page / "index.html").is_file():
                    errors.add(f"{file.relative_to(root)}: link to original course: {value}")
            return
        if not value.startswith("/") or value.startswith("//"):
            return
        path = unquote(urlsplit(value).path)
        if base and path != base and not path.startswith(base + "/"):
            errors.add(f"{file.relative_to(root)}: URL outside base path: {value}")
            return
        relative = path[len(base):].lstrip("/")
        target = root / relative
        exists = target.is_file() or (target / "index.html").is_file()
        if relative and not target.suffix:
            exists = exists or target.with_suffix(".html").is_file()
        if not exists:
            errors.add(f"{file.relative_to(root)}: missing target: {value}")

    for page in pages:
        parser = References()
        parser.feed(page.read_text(encoding="utf-8"))
        for value in parser.urls:
            check_url(page, value)
    for css in root.rglob("*.css"):
        for match in re.finditer(r"""url\(\s*['"]?([^'")\s]+)""", css.read_text(encoding="utf-8")):
            check_url(css, match.group(1))
    if errors:
        print("\n".join(sorted(errors)), file=sys.stderr)
        return 1
    print(f"Verified {len(pages)} HTML pages and root-relative asset URLs.")
    return 0


if __name__ == "__main__":
    sys.exit(check(Path(sys.argv[1]), sys.argv[2].rstrip("/")))
