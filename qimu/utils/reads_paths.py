"""Classes and utilities for handling sequencing reads."""

import os
import re
from collections import defaultdict
from enum import Enum
from pathlib import Path


class ReadType(Enum):
    """Type of sequencing reads."""

    SINGLE_END = "single-end"
    PAIRED_END = "paired-end"
    OTHER = "other"


class SequencedSample:
    """Represents a sequenced sample with its reads."""

    def __init__(
        self,
        sample_id: str,
        read_type: ReadType,
        reads: list[Path],
        pwd: Path | None = None,
    ):
        """Initialize a sequenced sample.

        Args:
            sample_id: Sample identifier
            read_type: Type of reads (SE/PE)
            reads: List of paths to read files (1 for SE, 2 for PE)
            pwd: Working directory when created (defaults to current)
        """
        self.id = sample_id
        self.type = read_type
        # Store absolute paths internally
        self.reads_absolute = [Path(r).resolve() for r in reads]
        self.pwd = pwd or Path.cwd()

        # Validate read count matches type
        if read_type == ReadType.SINGLE_END and len(reads) != 1:
            raise ValueError(f"Single-end sample must have 1 read file, got {len(reads)}")
        elif read_type == ReadType.PAIRED_END and len(reads) != 2:
            raise ValueError(f"Paired-end sample must have 2 read files, got {len(reads)}")

    def get_reads(self, absolute: bool = False, relative_to: Path | None = None) -> list[str]:
        """Get read paths.

        Args:
            absolute: Return absolute paths
            relative_to: Make paths relative to this directory (overrides absolute)

        Returns:
            List of read paths as strings
        """
        if relative_to:
            return [str(p.relative_to(relative_to)) for p in self.reads_absolute]
        elif absolute:
            return [str(p) for p in self.reads_absolute]
        else:
            # Relative to PWD
            return [str(p.relative_to(self.pwd)) for p in self.reads_absolute]

    def __repr__(self):
        return f"SequencedSample(id={self.id}, type={self.type.value}, reads={len(self.reads_absolute)})"


class SequencedRun:
    """Represents a collection of sequenced samples."""

    def __init__(self):
        """Initialize an empty sequenced run."""
        self.samples: list[SequencedSample] = []
        self._sample_ids: set[str] = set()

    def add_sample(self, sample: SequencedSample):
        """Add a sample to the run.

        Args:
            sample: SequencedSample to add

        Raises:
            ValueError: If sample ID already exists
        """
        if sample.id in self._sample_ids:
            raise ValueError(f"Duplicate sample ID: {sample.id}")

        self.samples.append(sample)
        self._sample_ids.add(sample.id)

    def validate_consistency(self):
        """Validate that all samples are consistent (all PE or all SE).

        Raises:
            ValueError: If mix of PE and SE samples found
        """
        if not self.samples:
            return

        types = {s.type for s in self.samples}
        if ReadType.SINGLE_END in types and ReadType.PAIRED_END in types:
            raise ValueError(
                "Mixed single-end and paired-end samples found. "
                "All samples must be of the same type."
            )

    def is_paired_end(self) -> bool:
        """Check if run contains paired-end samples.

        Returns:
            True if any sample is paired-end
        """
        return any(s.type == ReadType.PAIRED_END for s in self.samples)

    def to_table(
        self,
        separator: str = "\t",
        col_id: str = "SampleId",
        col_for: str = "reads_R1",
        col_rev: str = "reads_R2",
        absolute: bool = False,
    ) -> str:
        """Generate table representation of the run.

        Args:
            separator: Column separator
            col_id: Column name for sample ID
            col_for: Column name for forward reads
            col_rev: Column name for reverse reads
            absolute: Use absolute paths

        Returns:
            Table as string
        """
        if not self.samples:
            return ""

        is_pe = self.is_paired_end()

        # Build header
        if is_pe:
            header = separator.join([col_id, col_for, col_rev])
        else:
            header = separator.join([col_id, col_for])

        # Build rows
        rows = [header]
        for sample in sorted(self.samples, key=lambda s: s.id):
            reads = sample.get_reads(absolute=absolute)
            if is_pe:
                row = separator.join([sample.id, reads[0], reads[1]])
            else:
                row = separator.join([sample.id, reads[0]])
            rows.append(row)

        return "\n".join(rows)

    def __len__(self):
        return len(self.samples)

    def __repr__(self):
        return f"SequencedRun(samples={len(self.samples)})"


def strip_non_alphanumeric(text: str) -> str:
    """Strip non-alphanumeric characters from start and end of string.

    Args:
        text: String to strip

    Returns:
        Stripped string
    """
    # Remove non-alphanumeric from start
    text = re.sub(r"^[^a-zA-Z0-9]+", "", text)
    # Remove non-alphanumeric from end
    text = re.sub(r"[^a-zA-Z0-9]+$", "", text)
    return text


def extract_sample_name(
    filename: str,
    separators: list[str],
    forward_tags: list[str],
    reverse_tags: list[str],
    strip_strings: list[str],
) -> str:
    """Extract sample name from filename.

    Args:
        filename: Filename (without directory)
        separators: Characters to use for splitting
        forward_tags: Tags indicating forward reads
        reverse_tags: Tags indicating reverse reads
        strip_strings: Strings to remove from anywhere in name

    Returns:
        Extracted sample name
    """
    name = filename

    # Remove common file extensions
    extensions = [".fastq.gz", ".fq.gz", ".fastq", ".fq"]
    for ext in extensions:
        if name.endswith(ext):
            name = name[: -len(ext)]
            break

    # Remove all forward/reverse tags
    for tag in forward_tags + reverse_tags:
        name = name.replace(tag, "")

    # Apply strip strings
    for strip_str in strip_strings:
        name = name.replace(strip_str, "")

    # Split by separators and rejoin
    parts = [name]
    for sep in separators:
        new_parts = []
        for part in parts:
            new_parts.extend(part.split(sep))
        parts = new_parts

    # Rejoin with first separator
    sep = separators[0] if separators else "_"
    name = sep.join(parts)

    # Strip non-alphanumeric from start/end
    name = strip_non_alphanumeric(name)

    return name


def find_first_unique_parts(sample_names: list[str], separator: str = "_") -> dict[str, str]:
    """Find the first unique part of each sample name.

    Args:
        sample_names: List of sample names
        separator: Separator to use for splitting

    Returns:
        Dictionary mapping original name to unique part
    """
    if not sample_names:
        return {}

    # Split all names into parts
    name_parts = {}
    for name in sample_names:
        parts = name.split(separator)
        name_parts[name] = parts

    # Find first position where names differ
    result = {}
    for name, parts in name_parts.items():
        # Try each part until we find one that's unique
        for i, part in enumerate(parts):
            # Check if this part is unique among all samples
            unique = True
            for other_name, other_parts in name_parts.items():
                if other_name == name:
                    continue
                # If other sample has same part at same position, not unique
                if i < len(other_parts) and other_parts[i] == part:
                    unique = False
                    break

            if unique:
                result[name] = part
                break
        else:
            # If no unique part found, use entire name
            result[name] = name

    return result


def scan_directories(
    paths: list[Path],
    extensions: list[str],
    forward_tags: list[str],
    reverse_tags: list[str],
) -> dict[str, Path]:
    """Scan directories for read files.

    Args:
        paths: List of directories to scan
        extensions: Valid file extensions
        forward_tags: Tags indicating forward reads
        reverse_tags: Tags indicating reverse reads

    Returns:
        Dictionary mapping filename to absolute path
    """
    files = {}

    for path in paths:
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        # Scan directory (non-recursive)
        for file_path in path.iterdir():
            if not file_path.is_file():
                continue

            # Check extension
            filename = file_path.name
            has_valid_ext = any(filename.endswith(ext) for ext in extensions)
            if not has_valid_ext:
                continue

            files[filename] = file_path.resolve()

    return files


def pair_reads(
    files: dict[str, Path],
    forward_tags: list[str],
    reverse_tags: list[str],
    force_single_end: bool = False,
) -> tuple[dict[str, tuple[Path, Path | None]], list[str]]:
    """Pair forward and reverse reads.

    Args:
        files: Dictionary of filename to path
        forward_tags: Tags indicating forward reads
        reverse_tags: Tags indicating reverse reads
        force_single_end: Force all reads as single-end

    Returns:
        Tuple of (paired_reads, unpaired_files)
        paired_reads: Dict of base_name -> (forward_path, reverse_path or None)
        unpaired_files: List of filenames that couldn't be classified
    """
    forward_reads = {}
    reverse_reads = {}
    unpaired = []

    for filename, filepath in files.items():
        # Check if forward
        is_forward = any(tag in filename for tag in forward_tags)
        # Check if reverse
        is_reverse = any(tag in filename for tag in reverse_tags)

        if force_single_end or (not is_forward and not is_reverse):
            # Treat as single-end
            unpaired.append(filename)
        elif is_forward:
            # Remove forward tag to get base name
            base_name = filename
            for tag in forward_tags:
                base_name = base_name.replace(tag, "___PAIR___")
            forward_reads[base_name] = filepath
        elif is_reverse:
            # Remove reverse tag to get base name
            base_name = filename
            for tag in reverse_tags:
                base_name = base_name.replace(tag, "___PAIR___")
            reverse_reads[base_name] = filepath

    # Pair up forward and reverse
    paired = {}
    for base_name, forward_path in forward_reads.items():
        reverse_path = reverse_reads.get(base_name)
        paired[base_name] = (forward_path, reverse_path)

    # Add orphan reverse reads as unpaired
    for base_name, reverse_path in reverse_reads.items():
        if base_name not in forward_reads:
            unpaired.append(reverse_path.name)

    return paired, unpaired


def build_sequenced_run(
    paths: list[Path],
    extensions: list[str],
    forward_tags: list[str],
    reverse_tags: list[str],
    separators: list[str],
    strip_strings: list[str],
    force_single_end: bool = False,
) -> SequencedRun:
    """Build a SequencedRun from directory scanning.

    Args:
        paths: Directories to scan
        extensions: Valid file extensions
        forward_tags: Forward read tags
        reverse_tags: Reverse read tags
        separators: Characters for splitting sample names
        strip_strings: Strings to strip from sample names
        force_single_end: Force single-end mode

    Returns:
        SequencedRun object

    Raises:
        ValueError: If mix of PE and SE found
    """
    pwd = Path.cwd()
    run = SequencedRun()

    # Scan directories
    files = scan_directories(paths, extensions, forward_tags, reverse_tags)

    if not files:
        return run

    # Pair reads
    paired, unpaired = pair_reads(files, forward_tags, reverse_tags, force_single_end)

    # Process paired reads
    paired_samples = {}
    for base_name, (forward_path, reverse_path) in paired.items():
        # Extract sample name from forward read
        sample_name = extract_sample_name(
            forward_path.name, separators, forward_tags, reverse_tags, strip_strings
        )

        if reverse_path:
            # Paired-end
            paired_samples[sample_name] = (forward_path, reverse_path)
        else:
            # Forward only, treat as SE
            paired_samples[sample_name] = (forward_path,)

    # Process unpaired reads
    unpaired_samples = {}
    for filename in unpaired:
        sample_name = extract_sample_name(
            filename, separators, forward_tags, reverse_tags, strip_strings
        )
        unpaired_samples[sample_name] = (files[filename],)

    # Combine all samples
    all_samples = {}
    all_samples.update(paired_samples)
    all_samples.update(unpaired_samples)

    # Find first unique parts
    sep = separators[0] if separators else "_"
    unique_names = find_first_unique_parts(list(all_samples.keys()), sep)

    # Create SequencedSample objects
    for original_name, reads_tuple in all_samples.items():
        sample_id = unique_names.get(original_name, original_name)
        read_type = ReadType.PAIRED_END if len(reads_tuple) == 2 else ReadType.SINGLE_END

        sample = SequencedSample(
            sample_id=sample_id,
            read_type=read_type,
            reads=list(reads_tuple),
            pwd=pwd,
        )
        run.add_sample(sample)

    # Validate consistency
    run.validate_consistency()

    return run
