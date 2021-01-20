import argparse
import glob
import os
import sys

import ass

def main():
    parser = argparse.ArgumentParser(
        description="Create signs files for .ass files in a directory")
    parser.add_argument('directory', help="""
    Directory containing .ass files""")
    parser.add_argument('styles', help="""
    List of dialogue style names to remove (comma separated)""")
    args = parser.parse_args()

    styles = args.styles.split(',')

    for file in glob.glob(args.directory+"**/*.ass"):
        # Get base name
        base_name = os.path.splitext(file)[0]
        # Skip processing existing signs files
        if base_name.endswith("_signs"):
            continue
        # Parse sub file
        with open(os.path.join(args.directory, file), encoding='utf_8_sig') as subs:
            doc = ass.parse(subs)
        # Create list of sign events
        sign_events = []
        for event in doc.events:
            if event.style not in styles:
                sign_events.append(event)
        doc.events = sign_events
        # Create signs file
        signs_file = os.path.join(args.directory, base_name + "_signs.ass")
        with open(signs_file, 'w', encoding='utf_8_sig') as signs:
            doc.dump_file(signs)
        print(f"Created file {signs_file}")

if __name__ == "__main__":
    sys.exit(main())
