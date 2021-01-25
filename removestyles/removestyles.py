import argparse
import glob
import os
import sys

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
        "--remove",
        action="store_true",
        default=True,
        help="Remove lines with the specified style names (default option)",
    )
    group.add_argument(
        "--keep",
        action="store_true",
        default=False,
        help="Keep lines with the specified style names and remove the rest",
    )
    args = parser.parse_args()

    styles = args.styles.split(",")

    for file in glob.glob(args.directory + "/*.ass"):
        # Get base name
        base_name = os.path.splitext(file)[0]
        # Skip processing existing files created by the script
        if base_name.endswith(args.suffix):
            continue
        # Parse sub file
        with open(
            os.path.join(args.directory, file), encoding="utf_8_sig"
        ) as orig_subs:
            doc = ass.parse(orig_subs)
        # Create new events list and add items
        new_events = []
        for event in doc.events:
            if args.keep:
                # Only include events with specified styles
                if event.style in styles:
                    new_events.append(event)
            else:
                # Do not include events with specified styles
                if event.style not in styles:
                    new_events.append(event)
        # Overwrite events with the new list
        doc.events = new_events
        # Create new sub file
        new_file = os.path.join(
            args.directory, "{}_{}.ass".format(base_name, args.suffix)
        )
        with open(new_file, "w", encoding="utf_8_sig") as new_subs:
            doc.dump_file(new_subs)
        print(f"Created file {new_file}")


if __name__ == "__main__":
    sys.exit(main())
