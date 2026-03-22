"""Tests for the CLI entry point."""

import subprocess
import sys


class TestCliEntryPoint:
    def test_help_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "contrib_engine", "--help"],
            capture_output=True, text=True,
            cwd="/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here",
        )
        assert result.returncode == 0
        assert "scan" in result.stdout
        assert "campaign" in result.stdout

    def test_scan_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "contrib_engine", "scan", "--help"],
            capture_output=True, text=True,
            cwd="/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here",
        )
        assert result.returncode == 0
        assert "--no-github" in result.stdout

    def test_invalid_subcommand(self):
        result = subprocess.run(
            [sys.executable, "-m", "contrib_engine", "nonexistent"],
            capture_output=True, text=True,
            cwd="/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here",
        )
        assert result.returncode != 0

    def test_campaign_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "contrib_engine", "campaign", "--help"],
            capture_output=True, text=True,
            cwd="/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here",
        )
        assert result.returncode == 0

    def test_outreach_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "contrib_engine", "outreach", "--help"],
            capture_output=True, text=True,
            cwd="/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here",
        )
        assert result.returncode == 0

    def test_backflow_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "contrib_engine", "backflow", "--help"],
            capture_output=True, text=True,
            cwd="/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here",
        )
        assert result.returncode == 0


class TestPrefixParameter:
    def test_register_with_prefix(self):
        import argparse
        from contrib_engine.cli import register_contrib_commands
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_contrib_commands(subparsers, prefix="contrib-")
        args = parser.parse_args(["contrib-scan", "--no-github"])
        assert hasattr(args, "func")

    def test_register_without_prefix(self):
        import argparse
        from contrib_engine.cli import register_contrib_commands
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_contrib_commands(subparsers, prefix="")
        args = parser.parse_args(["scan", "--no-github"])
        assert hasattr(args, "func")
