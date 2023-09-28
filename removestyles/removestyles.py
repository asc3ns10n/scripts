import argparse
import os
import sys
from pathlib import Path

import ass


def main():
    parser = argparse.ArgumentParser(
        description="Remove lines from .ass files that use specific styles"
    )
    parser.add_argument(
        "--dir",
        required=True,
        dest="directory",
        metavar="<directory>",
        help="""
    Directory containing .ass files""",
    )
    parser.add_argument(
        "--styles",
        required=True,
        dest="styles",
        metavar="<csv>",
        help="""
    Comma separated list of style names""",
    )
    parser.add_argument(
        "--suffix",
        dest="suffix",
        metavar="<suffix>",
        default="new",
        help="""
    Text that will be appended to the new file name""",
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
        help="""
    Remove comments that use matching styles""",
    )

    args = parser.parse_args()
    directory_path = Path(args.directory)
    styles = args.styles.split(",")

    # Check if directory exists
    if not directory_path.exists() or not directory_path.is_dir():
        print(f"Error: Directory '{directory_path}' does not exist or is not a directory.", file=sys.stderr)
        return 1

    for file_path in directory_path.glob("*.ass"):
        base_name = file_path.stem

        # Skip processing existing files created by the script
        if base_name.endswith(args.suffix):
            continue

        # Parse sub file
        with file_path.open(encoding="utf_8_sig") as orig_subs:
            doc = ass.parse(orig_subs)
            
        # Filtering events based on user input
        new_events = []
        for event in doc.events:
            if args.keep_lines and event.style in styles:
                new_events.append(event)
            elif not args.keep_lines and event.style not in styles:
                new_events.append(event)
            elif event.TYPE == "Comment" and not args.remove_comments:
                new_events.append(event)
        
        doc.events = new_events

        new_file_path = directory_path / f"{base_name}_{args.suffix}.ass"
        with new_file_path.open("w", encoding="utf_8_sig") as new_subs:
            doc.dump_file(new_subs)

        print(f"Created file {new_file_path}")


if __name__ == "__main__":
    sys.exit(main())
