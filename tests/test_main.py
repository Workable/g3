from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from g3.main import MessageTone, app
from g3.services.generate.commit.messages.creator import Creator as CommitMessageCreator
from g3.services.generate.pr.messages.creator import Creator as PRMessageCreator

runner = CliRunner()
friendly_tone = MessageTone.FRIENDLY.value


class TestCommit:
    @pytest.fixture(scope="class", autouse=True)
    def creator(self):
        with patch.object(CommitMessageCreator, "create"):
            yield

    def test_commit(self):
        result = runner.invoke(app, ["commit"])
        assert result.exit_code == 0
        assert "Generating commit message with friendly tone.." in result.output

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
        result = runner.invoke(app, ["commit", "--edit", "ba8ab3d"])
        assert result.exit_code == 0
        assert "For existing commit: ba8ab3d" in result.output


class TestPR:
    @pytest.fixture(scope="class", autouse=True)
    def creator(self):
        with patch.object(PRMessageCreator, "create"):
            yield

    def test_pr(self):
        result = runner.invoke(app, ["pr"])
        assert result.exit_code == 0
        assert "Generating PR description with friendly tone.." in result.output

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
