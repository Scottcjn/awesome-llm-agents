from argparse import Namespace

import pytest

import update_metrics


class FixedDate:
    @classmethod
    def now(cls):
        return cls()

    def strftime(self, fmt):
        assert fmt == "%Y-%m-%d"
        return "2026-05-11"


def test_format_metrics_badges_uses_grouped_counts():
    metrics = {
        "stars": 12345,
        "forks": 6789,
        "contributors": 42,
        "open_issues": 7,
        "language": "Python",
        "license": "MIT",
    }

    assert update_metrics.format_metrics_badges(metrics) == (
        "12,345 stars \u00b7 6,789 forks \u00b7 42 contributors \u00b7 "
        "7 issues \u00b7 Python \u00b7 MIT"
    )


def test_get_repo_metrics_rejects_non_github_urls():
    assert update_metrics.get_repo_metrics("https://example.com/owner/repo") is None


def test_update_readme_with_metrics_rewrites_date_and_entry(tmp_path, monkeypatch):
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Agents (Last updated: 2026-03-15)\n\n"
        "## Frameworks\n\n"
        "- [Demo](https://github.com/example/demo) - Demo framework\n\n"
        "  1 stars \u00b7 1 forks \u00b7 1 contributors \u00b7 1 issues \u00b7 Go \u00b7 BSD\n\n"
        "  - Keeps existing feature bullets\n",
    )
    metrics = {
        "stars": 1000,
        "forks": 25,
        "contributors": 8,
        "open_issues": 3,
        "language": "Python",
        "license": "Apache-2.0",
    }

    monkeypatch.setattr(update_metrics, "datetime", FixedDate)
    monkeypatch.setattr(update_metrics, "get_repo_metrics", lambda url: metrics)

    update_metrics.update_readme_with_metrics(readme, Namespace(url=None, name=None))

    content = readme.read_text()
    assert "Last updated: 2026-05-11" in content
    assert (
        "1,000 stars \u00b7 25 forks \u00b7 8 contributors \u00b7 "
        "3 issues \u00b7 Python \u00b7 Apache-2.0"
    ) in content
    assert "1 stars \u00b7 1 forks" not in content
    assert "  - Keeps existing feature bullets" in content


def test_update_readme_with_metrics_requires_last_updated_marker(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Agents\n\n## Frameworks\n\n")

    with pytest.raises(Exception, match="Last updated"):
        update_metrics.update_readme_with_metrics(readme, Namespace(url=None, name=None))
