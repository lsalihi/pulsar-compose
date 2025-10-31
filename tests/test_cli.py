import os
from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture()
def temp_home(tmp_path, monkeypatch):
    # Redirect HOME so CLI config/history writes to a temp directory
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def test_cli_help(temp_home):
    from cli.main import cli

    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    # Help output contains program name and example usage
    assert "Pulsar Compose" in result.output
    assert "pulsar run" in result.output


def test_cli_version(temp_home):
    from cli.main import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "Pulsar Compose v" in result.output


def test_workflow_init_and_validate(temp_home):
    from cli.main import cli

    runner = CliRunner()
    wf_path = Path(temp_home) / "sample-workflow.yml"

    # Initialize a simple workflow template to a file under temp HOME
    result_init = runner.invoke(
        cli, ["workflow", "init", "simple", "--output", str(wf_path)]
    )
    assert result_init.exit_code == 0
    assert wf_path.exists()

    # Validate the generated workflow file
    result_validate = runner.invoke(cli, ["validate", str(wf_path)])
    assert result_validate.exit_code == 0
    assert "Workflow file is valid" in result_validate.output
