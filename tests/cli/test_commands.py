from click.testing import CliRunner
from arkitekt_next.cli.main import cli
import os
from unittest.mock import patch

def test_init_uv():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
            mock_which.return_value = "/usr/bin/uv"
            
            result = runner.invoke(cli, ["init", "--package-manager", "uv", "--identifier", "com.test.app", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"])
            if result.exit_code != 0:
                print(result.output)
                print(result.exception)
            assert result.exit_code == 0
            
            # Verify uv commands were called
            assert mock_run.call_count == 2
            mock_run.assert_any_call(["uv", "init", "--name", "com.test.app", "--no-workspace"], check=True, cwd=os.getcwd())
            mock_run.assert_any_call(["uv", "add", "arkitekt-next"], check=True, cwd=os.getcwd())
            
            assert os.path.exists("app.py")
            assert os.path.exists(".arkitekt_next/manifest.yaml")
            
            with open(".arkitekt_next/manifest.yaml") as f:
                content = f.read()
                assert "package_manager: uv" in content

def test_init_yes():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Should not prompt for anything
        result = runner.invoke(cli, ["init", "--yes", "--package-manager", "pip"])
        if result.exit_code != 0:
            print(result.output)
            print(result.exception)
        assert result.exit_code == 0
        assert os.path.exists("app.py")
        assert os.path.exists(".arkitekt_next/manifest.yaml")

def test_init_path():
    runner = CliRunner()
    with runner.isolated_filesystem():
        original_cwd = os.getcwd()
        # Explicitly use pip to avoid uv dependency in this test
        # We don't provide identifier, so it should default to "myapp" (basename of path)
        # We need to provide input for the prompt because even with default, click.prompt waits for input if not provided via args
        result = runner.invoke(cli, ["init", "myapp", "--package-manager", "pip", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"], input="\n")
        if result.exit_code != 0:
            print(result.output)
            print(result.exception)
        assert result.exit_code == 0
        
        # Check relative to the original directory
        assert os.path.exists(os.path.join(original_cwd, "myapp", "app.py"))
        assert os.path.exists(os.path.join(original_cwd, "myapp", ".arkitekt_next", "manifest.yaml"))
        
        # Check if identifier was correctly set to myapp
        with open(os.path.join(original_cwd, "myapp", ".arkitekt_next", "manifest.yaml")) as f:
            content = f.read()
            assert "identifier: myapp" in content

def test_init_default_uv():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
            # Simulate uv being installed
            mock_which.return_value = "/usr/bin/uv"
            
            # Do not specify package manager, should default to uv
            result = runner.invoke(cli, ["init", "--identifier", "com.test.app", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"])
            
            assert result.exit_code == 0
            # Verify uv commands were called
            assert mock_run.call_count == 2
            mock_run.assert_any_call(["uv", "init", "--name", "com.test.app", "--no-workspace"], check=True, cwd=os.getcwd())

def test_init_default_pip():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with patch("shutil.which") as mock_which:
            # Simulate uv NOT being installed
            mock_which.return_value = None
            
            # Do not specify package manager, should default to pip
            result = runner.invoke(cli, ["init", "--identifier", "com.test.app", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"])
            
            assert result.exit_code == 0
            assert os.path.exists("app.py")
            # Should NOT have pyproject.toml from uv
            assert not os.path.exists("pyproject.toml")

def test_init_uv_not_installed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            
            result = runner.invoke(cli, ["init", "--package-manager", "uv", "--identifier", "com.test.app", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"])
            assert result.exit_code != 0
            assert "uv is not installed" in result.output

def test_kabinet_init():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # First we need a manifest
        runner.invoke(cli, ["init", "--identifier", "com.test.app", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"])
        
        result = runner.invoke(cli, ["kabinet", "init", "--flavour", "vanilla", "--devcontainer", "--arkitekt-version", "0.0.1"])
        if result.exit_code != 0:
            print(result.output)
            print(result.exception)
        assert result.exit_code == 0
        assert os.path.exists(".arkitekt_next/flavours/vanilla/Dockerfile")
        assert os.path.exists(".devcontainer/vanilla/devcontainer.json")
        
        with open(".devcontainer/vanilla/devcontainer.json") as f:
            content = f.read()
            assert "ms-python.python" in content

def test_kabinet_init_uv():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # First we need a manifest with uv
        runner.invoke(cli, ["init", "--package-manager", "uv", "--identifier", "com.test.app", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"])
        
        # Run kabinet init without specifying template, should pick uv
        result = runner.invoke(cli, ["kabinet", "init", "--flavour", "uv_flavour", "--devcontainer", "--arkitekt-version", "0.0.1"])
        if result.exit_code != 0:
            print(result.output)
            print(result.exception)
        assert result.exit_code == 0
        assert os.path.exists(".arkitekt_next/flavours/uv_flavour/Dockerfile")
        
        # Check if the generated Dockerfile contains uv specific instructions
        with open(".arkitekt_next/flavours/uv_flavour/Dockerfile") as f:
            content = f.read()
            assert "COPY --from=ghcr.io/astral-sh/uv" in content

def test_kabinet_flavour_commands():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Initialize project
        runner.invoke(cli, ["init", "--identifier", "com.test.app", "--version", "0.0.1", "--author", "me", "--entrypoint", "app"])
        
        # Test flavour add (alias for init)
        result = runner.invoke(cli, ["kabinet", "flavour", "add", "--flavour", "gpu", "--description", "GPU flavour"], input="n\n")
        if result.exit_code != 0:
            print(result.output)
            print(result.exception)
        assert result.exit_code == 0
        assert os.path.exists(".arkitekt_next/flavours/gpu/config.yaml")
        
        # Test selector add
        result = runner.invoke(cli, ["kabinet", "selector", "add", "gpu", "--kind", "cuda", "--cuda-cores", "100"])
        if result.exit_code != 0:
            print(result.output)
            print(result.exception)
        assert result.exit_code == 0
        
        # Verify selector was added
        with open(".arkitekt_next/flavours/gpu/config.yaml") as f:
            content = f.read()
            assert "kind: cuda" in content
            assert "cuda_cores: 100" in content
