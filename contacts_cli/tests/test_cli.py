"""Tests for CLI layer."""

import sqlite3
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from contacts_cli.cli import app


runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_run_command(self):
        """Test run command with valid input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"

            # Create source database
            conn = sqlite3.connect(source_db)
            conn.execute("""
                CREATE TABLE raw_contacts (
                    contact_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    email TEXT
                )
            """)
            conn.execute("""
                INSERT INTO raw_contacts (contact_id, full_name, email)
                VALUES (1, 'Alice Chen', 'alice@example.com')
            """)
            conn.commit()
            conn.close()

            # Run CLI
            result = runner.invoke(app, ["run", str(source_db), str(target_db)])

            assert result.exit_code == 0
            # Check that target database was created
            assert target_db.exists()

    def test_cli_run_missing_source(self):
        """Test run command with missing source file."""
        result = runner.invoke(app, ["run", "nonexistent.sqlite", "output.sqlite"])

        assert result.exit_code == 1

    def test_cli_create_sample_command(self):
        """Test create-sample command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_db = Path(tmpdir) / "sample.sqlite"

            # Run CLI
            result = runner.invoke(app, ["create-sample", str(output_db)])

            assert result.exit_code == 0
            assert output_db.exists()

            # Verify data
            conn = sqlite3.connect(output_db)
            cursor = conn.execute("SELECT COUNT(*) FROM raw_contacts")
            count = cursor.fetchone()[0]
            conn.close()

            assert count == 5
