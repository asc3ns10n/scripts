import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Set

import ass
from tqdm import tqdm

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

def validate_styles(styles: Set[str], doc: ass.Document) -> bool:
    """Validate that all specified styles exist in the document."""
    existing_styles = {style.name for style in doc.styles}
    invalid_styles = styles - existing_styles
    if invalid_styles:
        logging.warning(f"The following styles were not found: {', '.join(invalid_styles)}")
        return False
    return True

def process_file(
    file_path: Path,
    styles: Set[str],
    suffix: str,
    keep_lines: bool,
    remove_comments: bool
) -> None:
    """Process a single ASS file."""
    try:
        with file_path.open(encoding="utf_8_sig") as orig_subs:
            doc = ass.parse(orig_subs)
    except (UnicodeError, ass.ParseError) as e:
        logging.error(f"Failed to parse {file_path}: {e}")
        return
    except OSError as e:
        logging.error(f"Failed to open {file_path}: {e}")
        return

    validate_styles(styles, doc)

    # Filtering events based on user input
    new_events = [
        event for event in doc.events
        if (keep_lines and event.style in styles) or
           (not keep_lines and event.style not in styles) or
           (event.TYPE == "Comment" and not remove_comments)
    ]
    
    doc.events = new_events

    new_file_path = file_path.parent / f"{file_path.stem}_{suffix}.ass"
    try:
        with new_file_path.open("w", encoding="utf_8_sig") as new_subs:
            doc.dump_file(new_subs)
        logging.info(f"Created file {new_file_path}")
    except OSError as e:
        logging.error(f"Failed to write {new_file_path}: {e}")

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove lines from .ass files that use specific styles"
    )
    parser.add_argument(
        "--dir",
        required=True,
        dest="directory",
        metavar="<directory>",
        type=Path,
        help="Directory containing .ass files",
    )
    parser.add_argument(
        "--styles",
        required=True,
        dest="styles",
        metavar="<csv>",
        help="Comma separated list of style names",
    )
    parser.add_argument(
        "--suffix",
        dest="suffix",
        metavar="<suffix>",
        default="new",
        help="Text that will be appended to the new file name",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--remove-lines",
        action="store_true",
        default=True,
        help="Remove lines with the specified style names (default option)",
    )
    group.add_argument(
        "--keep-lines",
        action="store_true",
        default=False,
        help="Keep lines with the specified style names and remove the rest",
    )
    parser.add_argument(
        "--remove-comments",
        action="store_true",
        default=False,
        help="Remove comments that use matching styles",
    )

    args = parser.parse_args()
    setup_logging()

    # Check if directory exists
    if not args.directory.exists() or not args.directory.is_dir():
        logging.error(f"Directory '{args.directory}' does not exist or is not a directory.")
        return 1

    styles = {style.strip() for style in args.styles.split(",")}
    if not styles:
        logging.error("No valid styles provided")
        return 1

    ass_files = list(args.directory.glob("*.ass"))
    if not ass_files:
        logging.warning(f"No .ass files found in {args.directory}")
        return 0

    # Process files with progress bar
    for file_path in tqdm(ass_files, desc="Processing files"):
        # Skip processing existing files created by the script
        if file_path.stem.endswith(args.suffix):
            continue
            
        process_file(
            file_path,
            styles,
            args.suffix,
            args.keep_lines,
            args.remove_comments
        )

    return 0

if __name__ == "__main__":
    sys.exit(main())
