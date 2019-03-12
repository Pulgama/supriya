import io
import unittest.mock

import pytest
import uqbar.io

import supriya.cli


def test_success(cli_paths):
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    session_path = pytest.helpers.create_cli_session(
        cli_paths.test_directory_path, "test_session"
    )
    script = supriya.cli.ManageSessionScript()
    command = ["--edit", "test_session"]
    mock_path = "supriya.cli.ProjectPackageScript._call_subprocess"
    with unittest.mock.patch(mock_path) as mock:
        mock.return_value = 0
        with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
            cli_paths.inner_project_path
        ):
            try:
                script(command)
            except SystemExit as exception:
                if exception.args[0]:
                    raise RuntimeError("SystemExit: {}".format(exception.code))
    pytest.helpers.compare_strings(
        r"""
        Edit candidates: 'test_session' ...
        """,
        string_io.getvalue(),
    )
    definition_path = session_path.joinpath("definition.py")
    command = "{} {!s}".format(
        supriya.config.get("core", "editor", fallback="vim"), definition_path
    )
    mock.assert_called_with(command)
