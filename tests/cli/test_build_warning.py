import pytest
import tempfile
import os
import yaml
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from arkitekt_next.cli.commands.kabinet.io import check_if_build_already_exists
from arkitekt_next.cli.commands.kabinet.types import Build, BuildsConfigFile
from arkitekt_next.cli.types import Manifest
from kabinet.api.schema import ManifestInput


class TestBuildWarning:
    """Test cases for build warning functionality"""

    def test_check_if_build_already_exists_no_file(self):
        """Test when no builds.yaml file exists"""
        manifest = Manifest(
            identifier="test.app",
            version="1.0.0",
            author="test",
            entrypoint="main.py",
            scopes=["read"]
        )

        with patch('arkitekt_next.cli.commands.kabinet.io.create_arkitekt_next_folder') as mock_folder:
            mock_folder.return_value = "/non/existent/path"
            result = check_if_build_already_exists(manifest, "vanilla")
            assert result is False

    def test_check_if_build_already_exists_empty_file(self):
        """Test when builds.yaml exists but is empty"""
        manifest = Manifest(
            identifier="test.app",
            version="1.0.0",
            author="test",
            entrypoint="main.py",
            scopes=["read"]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            builds_file = os.path.join(temp_dir, "builds.yaml")
            
            # Create empty config
            config = BuildsConfigFile(builds=[], latest_build_run=None)
            with open(builds_file, "w") as f:
                yaml.safe_dump(
                    json.loads(config.model_dump_json(exclude_none=True, exclude_unset=True, by_alias=True)),
                    f,
                )

            with patch('arkitekt_next.cli.commands.kabinet.io.create_arkitekt_next_folder') as mock_folder:
                mock_folder.return_value = temp_dir
                result = check_if_build_already_exists(manifest, "vanilla")
                assert result is False

    def test_check_if_build_already_exists_with_matching_build(self):
        """Test when a matching build exists"""
        manifest = Manifest(
            identifier="test.app",
            version="1.0.0",
            author="test",
            entrypoint="main.py",
            scopes=["read"]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            builds_file = os.path.join(temp_dir, "builds.yaml")
            
            # Create a test build with matching criteria
            manifest_input = ManifestInput(
                identifier="test.app",
                version="1.0.0",
                author="test",
                entrypoint="main.py",
                scopes=["read"]
            )
            
            test_build = Build(
                build_run="test-run-1",
                build_id="test-build-1",
                flavour="vanilla",
                manifest=manifest_input,
                selectors=[],
                description="Test build",
                build_at=datetime.now()
            )
            
            config = BuildsConfigFile(builds=[test_build], latest_build_run="test-run-1")
            
            with open(builds_file, "w") as f:
                yaml.safe_dump(
                    json.loads(config.model_dump_json(exclude_none=True, exclude_unset=True, by_alias=True)),
                    f,
                )

            with patch('arkitekt_next.cli.commands.kabinet.io.create_arkitekt_next_folder') as mock_folder:
                mock_folder.return_value = temp_dir
                result = check_if_build_already_exists(manifest, "vanilla")
                assert result is True

    def test_check_if_build_already_exists_different_flavour(self):
        """Test when build exists but for different flavour"""
        manifest = Manifest(
            identifier="test.app",
            version="1.0.0",
            author="test",
            entrypoint="main.py",
            scopes=["read"]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            builds_file = os.path.join(temp_dir, "builds.yaml")
            
            # Create a test build with different flavour
            manifest_input = ManifestInput(
                identifier="test.app",
                version="1.0.0",
                author="test",
                entrypoint="main.py",
                scopes=["read"]
            )
            
            test_build = Build(
                build_run="test-run-1",
                build_id="test-build-1",
                flavour="gpu",  # Different flavour
                manifest=manifest_input,
                selectors=[],
                description="Test build",
                build_at=datetime.now()
            )
            
            config = BuildsConfigFile(builds=[test_build], latest_build_run="test-run-1")
            
            with open(builds_file, "w") as f:
                yaml.safe_dump(
                    json.loads(config.model_dump_json(exclude_none=True, exclude_unset=True, by_alias=True)),
                    f,
                )

            with patch('arkitekt_next.cli.commands.kabinet.io.create_arkitekt_next_folder') as mock_folder:
                mock_folder.return_value = temp_dir
                result = check_if_build_already_exists(manifest, "vanilla")
                assert result is False

    def test_check_if_build_already_exists_different_version(self):
        """Test when build exists but for different version"""
        manifest = Manifest(
            identifier="test.app",
            version="2.0.0",  # Different version
            author="test",
            entrypoint="main.py",
            scopes=["read"]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            builds_file = os.path.join(temp_dir, "builds.yaml")
            
            # Create a test build with different version
            manifest_input = ManifestInput(
                identifier="test.app",
                version="1.0.0",  # Different version
                author="test",
                entrypoint="main.py",
                scopes=["read"]
            )
            
            test_build = Build(
                build_run="test-run-1",
                build_id="test-build-1",
                flavour="vanilla",
                manifest=manifest_input,
                selectors=[],
                description="Test build",
                build_at=datetime.now()
            )
            
            config = BuildsConfigFile(builds=[test_build], latest_build_run="test-run-1")
            
            with open(builds_file, "w") as f:
                yaml.safe_dump(
                    json.loads(config.model_dump_json(exclude_none=True, exclude_unset=True, by_alias=True)),
                    f,
                )

            with patch('arkitekt_next.cli.commands.kabinet.io.create_arkitekt_next_folder') as mock_folder:
                mock_folder.return_value = temp_dir
                result = check_if_build_already_exists(manifest, "vanilla")
                assert result is False