import pytest
from typer.testing import CliRunner

from g3.main import MessageTone, app

runner = CliRunner()


class TestCommit:
    def test_commit(self):
        result = runner.invoke(app, ["commit"])
        assert result.exit_code == 0
        assert "Generating commit message with friendly tone" in result.output

    @pytest.mark.parametrize("tone", MessageTone)
    def test_commit_tone(self, tone):
        result = runner.invoke(app, ["commit", "--tone", tone.value])
        assert result.exit_code == 0
        assert f"Generating commit message with {tone.value} tone" in result.output

    def test_commit_jira(self):
        result = runner.invoke(app, ["commit", "--jira", "G3-123"])
        assert result.exit_code == 0
        assert "Referencing Jira ticket: G3-123" in result.output

    def test_commit_include(self):
        result = runner.invoke(app, ["commit", "--include", "This is a test"])
        assert result.exit_code == 0
        assert "Including additional text:\nThis is a test" in result.output

    def test_commit_edit(self):
        result = runner.invoke(app, ["commit", "--edit", "1234567890"])
        assert result.exit_code == 0
        assert "For existing commit: 1234567890" in result.output


class TestPR:
    def test_pr(self):
        result = runner.invoke(app, ["pr"])
        assert result.exit_code == 0
        assert "Generating PR description with friendly tone" in result.output

    @pytest.mark.parametrize("tone", MessageTone)
    def test_pr_tone(self, tone):
        result = runner.invoke(app, ["pr", "--tone", tone.value])
        assert result.exit_code == 0
        assert f"Generating PR description with {tone.value} tone" in result.output

    def test_pr_jira(self):
        result = runner.invoke(app, ["pr", "--jira", "G3-123"])
        assert result.exit_code == 0
        assert "Referencing Jira ticket: G3-123" in result.output

    def test_pr_include(self):
        result = runner.invoke(app, ["pr", "--include", "This is a test"])
        assert result.exit_code == 0
        assert "Including additional text:\nThis is a test" in result.output

    def test_pr_edit(self):
        result = runner.invoke(app, ["pr", "--edit", "1234567890"])
        assert result.exit_code == 0
        assert "For previous PR: 1234567890" in result.output
