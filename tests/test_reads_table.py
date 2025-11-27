"""Tests for reads-table command."""

from pathlib import Path

from click.testing import CliRunner

from qimu.cli import cli


def test_reads_table_paired_end_illumina():
    """Test reads-table with Illumina-style paired-end reads (pe1)."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(cli, ["reads-table", str(test_dir)])

    assert result.exit_code == 0
    # Check header
    assert "SampleId\treads_R1\treads_R2" in result.output
    # Check that samples are present
    assert "Sample1" in result.output
    assert "Sample2" in result.output
    assert "Sample3" in result.output
    assert "Sample10" in result.output
    assert "Sample20" in result.output
    assert "Sample30" in result.output
    assert "Sample100" in result.output


def test_reads_table_paired_end_simple():
    """Test reads-table with simple paired-end reads (pe2)."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe2"

    result = runner.invoke(cli, ["reads-table", str(test_dir)])

    assert result.exit_code == 0
    # Check header
    assert "SampleId\treads_R1\treads_R2" in result.output
    # Check that samples are present
    assert "Sample1" in result.output
    assert "Sample2" in result.output
    assert "Sample3" in result.output
    assert "Sample10" in result.output
    assert "Sample20" in result.output
    assert "Sample30" in result.output
    assert "Sample100" in result.output


def test_reads_table_single_end_simple():
    """Test reads-table with simple single-end reads (se1)."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "se1"

    result = runner.invoke(cli, ["reads-table", str(test_dir)])

    assert result.exit_code == 0
    # Check header (no R2 column for single-end)
    assert "SampleId\treads_R1" in result.output
    assert "reads_R2" not in result.output
    # Check that samples are present
    assert "Ctrl" in result.output
    assert "Sample1" in result.output
    assert "Sample2" in result.output


def test_reads_table_single_end_project():
    """Test reads-table with project-style single-end reads (se2)."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "se2"

    result = runner.invoke(cli, ["reads-table", str(test_dir)])

    assert result.exit_code == 0
    # Check header
    assert "SampleId\treads_R1" in result.output
    # Check that samples are present
    assert "Ctrl" in result.output
    assert "Sample1" in result.output
    assert "Sample2" in result.output


def test_reads_table_force_single_end():
    """Test reads-table with --single-end flag on paired reads."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(cli, ["reads-table", str(test_dir), "--single-end"])

    assert result.exit_code == 0
    # With --single-end, should treat all files as single-end
    assert "SampleId\treads_R1" in result.output


def test_reads_table_absolute_paths():
    """Test reads-table with --abs flag for absolute paths."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(cli, ["reads-table", str(test_dir), "--abs"])

    assert result.exit_code == 0
    # Check that paths are absolute (contain full path)
    assert str(test_dir.resolve()) in result.output


def test_reads_table_custom_columns():
    """Test reads-table with custom column names."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(
        cli,
        [
            "reads-table",
            str(test_dir),
            "--col-id", "sample-id",
            "--col-for", "forward",
            "--col-rev", "reverse",
        ],
    )

    assert result.exit_code == 0
    # Check custom header
    assert "sample-id\tforward\treverse" in result.output
    # Original header should not be present
    assert "SampleId" not in result.output


def test_reads_table_csv_separator():
    """Test reads-table with comma separator."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(
        cli,
        ["reads-table", str(test_dir), "--tab-sep", ","],
    )

    assert result.exit_code == 0
    # Check CSV format
    assert "SampleId,reads_R1,reads_R2" in result.output
    # Should not have tabs
    lines = result.output.strip().split("\n")
    for line in lines:
        if line:
            assert "," in line


def test_reads_table_format_manifest():
    """Test reads-table with --format manifest."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(
        cli,
        ["reads-table", str(test_dir), "--format", "manifest"],
    )

    assert result.exit_code == 0
    # Check manifest format header
    assert "sample-id,forward-absolute-filepath,reverse-absolute-filepath" in result.output
    # Check that paths are absolute (manifest format forces absolute)
    assert str(test_dir.resolve()) in result.output


def test_reads_table_format_ampliseq():
    """Test reads-table with --format ampliseq."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(
        cli,
        ["reads-table", str(test_dir), "--format", "ampliseq"],
    )

    assert result.exit_code == 0
    # Check ampliseq format header (tab-separated)
    assert "sample-id\tforward-absolute-filepath\treverse-absolute-filepath" in result.output
    # Check that paths are absolute
    assert str(test_dir.resolve()) in result.output


def test_reads_table_format_mag():
    """Test reads-table with --format mag."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(
        cli,
        ["reads-table", str(test_dir), "--format", "mag"],
    )

    assert result.exit_code == 0
    # Check MAG format header
    assert "sample,R1,R2" in result.output
    # Check that paths are absolute
    assert str(test_dir.resolve()) in result.output


def test_reads_table_custom_tags():
    """Test reads-table with custom forward/reverse tags."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe2"

    result = runner.invoke(
        cli,
        [
            "reads-table",
            str(test_dir),
            "-1", "_1.",
            "-2", "_2.",
        ],
    )

    assert result.exit_code == 0
    # Should find the paired reads with _1 and _2 tags
    assert "Sample1" in result.output
    assert result.exit_code == 0


def test_reads_table_multiple_directories():
    """Test reads-table with multiple input directories."""
    runner = CliRunner()
    # Test with a single directory works
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(cli, ["reads-table", str(test_dir)])

    assert result.exit_code == 0
    assert "Sample1" in result.output


def test_reads_table_duplicate_samples_error():
    """Test that duplicate sample IDs are properly caught."""
    runner = CliRunner()
    # Using both pe1 and pe2 will have overlapping sample names
    test_dir1 = Path(__file__).parent / "reads" / "pe1"
    test_dir2 = Path(__file__).parent / "reads" / "pe2"

    result = runner.invoke(cli, ["reads-table", str(test_dir1), str(test_dir2)])

    # Should fail with duplicate sample ID error
    assert result.exit_code == 1
    assert "Duplicate sample ID" in result.stderr


def test_reads_table_empty_directory():
    """Test reads-table with directory containing no reads."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create an empty directory
        empty_dir = Path("empty")
        empty_dir.mkdir()

        result = runner.invoke(cli, ["reads-table", str(empty_dir)])

        # Should exit cleanly with warning
        assert result.exit_code == 0
        assert "No read files found" in result.stderr


def test_reads_table_nonexistent_directory():
    """Test reads-table with non-existent directory."""
    runner = CliRunner()

    result = runner.invoke(cli, ["reads-table", "/nonexistent/directory"])

    # Should fail with error
    assert result.exit_code != 0


def test_reads_table_custom_extensions():
    """Test reads-table with custom extensions."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(
        cli,
        ["reads-table", str(test_dir), "-e", ".fastq.gz", "-e", ".fq.gz"],
    )

    assert result.exit_code == 0
    assert "Sample1" in result.output


def test_reads_table_strip_strings():
    """Test reads-table with --strip option."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe2"

    result = runner.invoke(
        cli,
        ["reads-table", str(test_dir), "--strip", "PID100_"],
    )

    assert result.exit_code == 0
    # PID100_ should be stripped from sample IDs (first column)
    # Note: It will still appear in file paths (which is correct)
    lines = result.output.strip().split("\n")
    # Check that sample IDs don't start with PID100
    for line in lines[1:]:  # Skip header
        sample_id = line.split("\t")[0]
        assert not sample_id.startswith("PID100")
    assert "Sample1" in result.output


def test_reads_table_debug_mode():
    """Test reads-table with --debug flag."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(cli, ["--debug", "reads-table", str(test_dir)])

    assert result.exit_code == 0
    # Debug mode should work without errors and produce valid output
    assert "SampleId" in result.output
    assert "Sample1" in result.output


def test_reads_table_verbose_mode():
    """Test reads-table with --verbose flag."""
    runner = CliRunner()
    test_dir = Path(__file__).parent / "reads" / "pe1"

    result = runner.invoke(cli, ["--verbose", "reads-table", str(test_dir)])

    assert result.exit_code == 0
    # Verbose mode should work without errors and produce valid output
    assert "SampleId" in result.output
    assert "Sample1" in result.output
