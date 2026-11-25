"""Regression tests for the Pages export URL checker."""
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "check_pages_export", Path(__file__).with_name("check-pages-export.py")
)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ExportCheckTests(unittest.TestCase):
    def test_connection_hints_are_not_file_references(self):
        parser = checker.References()
        parser.feed('<link rel="preconnect" href="/" crossorigin="anonymous">'
                    '<link rel="dns-prefetch" href="/">'
                    '<link rel="stylesheet" href="/project/style.css">'
                    '<a href="/">Home</a><img src="/project/missing.png">')
        self.assertEqual(parser.urls, [
            "/project/style.css", "/", "/project/missing.png"
        ])

    def test_export_checks_routes_and_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for course in ("dagster-essentials", "dagster-etl", "dagster-dbt",
                           "dagster-testing", "ai-driven-data-engineering"):
                (root / course).mkdir()
                (root / course / "index.html").write_text("", encoding="utf-8")
            (root / "style.css").write_text("", encoding="utf-8")
            index = root / "index.html"
            index.write_text(
                '<link rel="preconnect" href="/">'
                '<link rel="stylesheet" href="/project/style.css">'
                '<a href="/project/dagster-etl/">Course</a>', encoding="utf-8"
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(checker.check(root, "/project"), 0)
            with index.open("a", encoding="utf-8") as f:
                f.write('<a href="/">Wrong root</a>'
                        '<a href="/project/dagster-etl.md">Wrong route</a>'
                        '<img src="/project/missing.png">')
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(checker.check(root, "/project"), 1)
            for error in ("URL outside base path: /",
                          "missing target: /project/dagster-etl.md",
                          "missing target: /project/missing.png"):
                self.assertIn(error, stderr.getvalue())

    def test_translated_course_links_must_be_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for course in ("dagster-essentials", "dagster-etl", "dagster-dbt",
                           "dagster-testing", "ai-driven-data-engineering"):
                (root / course).mkdir()
                (root / course / "index.html").write_text("", encoding="utf-8")
            lesson = root / "dagster-etl" / "lesson-1"
            lesson.mkdir()
            (lesson / "index.html").write_text("", encoding="utf-8")
            index = root / "index.html"
            index.write_text(
                '<a href="/project/dagster-etl/">Russian course</a>'
                '<a href="https://docs.dagster.io/guides/build/components/">Docs</a>'
                '<a href="https://courses.dagster.io/courses/untranslated">Other course</a>',
                encoding="utf-8"
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(checker.check(root, "/project"), 0)
            with index.open("a", encoding="utf-8") as f:
                f.write('<a href="https://courses.dagster.io/courses/dagster-etl">Original</a>'
                        '<a href="https://dagster-university.dagster-docs.io/dagster-etl/lesson-1/">Original lesson</a>')
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(checker.check(root, "/project"), 1)
            self.assertEqual(stderr.getvalue().count("link to original course:"), 2)


if __name__ == "__main__":
    unittest.main()
