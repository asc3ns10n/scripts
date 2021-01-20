# My Scripts

## Create Signs Subs

### Overview

Parses .ass files in a directory and creates files without dialogue lines. 

```
$ create_signs_subs --help
usage: create_signs_subs [-h] directory styles

Create signs files for .ass files in a directory

positional arguments:
  directory   Directory containing .ass files
  styles      List of dialogue style names to remove (comma separated)

optional arguments:
  -h, --help  show this help message and exit
  ```

Example: ```create_signs_subs "D:\Projects\Show\Subs" "Main,Italics"```

### Installation

```
pip install --user git+https://github.com/asc3ns10n/scripts/#subdirectory=create_signs_subs
```
