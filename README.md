# My Scripts

## Remove Styles

### Overview

Parses .ass files in a directory and removes lines that use specific styles. You can set it to keep or remove lines with specific style names. Useful for creating signs/songs files. 

```
$ removestyles --help
usage: removestyles.py [-h] --dir <directory> --styles <csv> [--suffix <suffix>] [--remove-lines | --keep-lines]
                       [--remove-comments]

Remove lines from .ass files that use specific styles

optional arguments:
  -h, --help         show this help message and exit
  --dir <directory>  Directory containing .ass files
  --styles <csv>     Comma separated list of style names
  --suffix <suffix>  Text that will be appended to the new file name
  --remove-lines     Remove lines with the specified style names (default option)
  --keep-lines       Keep lines with the specified style names and remove the rest
  --remove-comments  Remove comments that use matching styles 
```

### Installation

```
pip install --user git+https://github.com/asc3ns10n/scripts/#subdirectory=removestyles
```

### Examples

Create signs/songs file by removing all dialogue lines
```
removestyles --dir "D:\Projects\Show\Subs" --styles "Main,Italics" --suffix "signs"
```

Create file that only contains a specific style
```
removestyles --dir "D:\Projects\Show\Subs" --styles "Signs" --keep-lines
```

## Sync Audio

### Overview

Uses [cross correlation](https://en.wikipedia.org/wiki/Cross-correlation) to determine the offset between two audio files, and outputs a .mka file with the offset applied (no conversion). Functions similary to eXmendiC's [script](https://github.com/eXmendiC/Subfix-Pack/blob/master/Shift_AudioToBD.bat). Includes an additional option "--apply-to"  which can be used to apply the offset to a different file (ex. English dub).

**Note**: It is only able to account for a single offset. If multiple shifts are needed, you will need to use another tool ([vfr](https://github.com/wiiaboo/vfr)/[acsuite](https://github.com/OrangeChannel/acsuite)) or make manual adjustments in an editor.

```
$ syncaudio --help
usage: syncaudio [-h] --src <filename> --dst <filename> [--apply-to <filename>] [--trim <seconds>] [--sample-rate <rate>]

Find offset between two audio tracks and sync them

optional arguments:
  -h, --help            show this help message and exit
  --src <filename>      Audio file that has desired sync
  --dst <filename>      Audio file to be synced
  --apply-to <filename>
                        File to apply offset to
  --trim <seconds>      Only uses first n seconds of audio files [900]
  --sample-rate <rate>  Target sample rate during downsampling [8000]
```

### Installation

```
pip install --user git+https://github.com/asc3ns10n/scripts/#subdirectory=syncaudio
```
You also need to have [ffmpeg](https://ffmpeg.org/) and [mkvmerge](https://mkvtoolnix.download/) installed, and they need to be included in your PATH enviroment variable. 

### Examples

Do a simple sync between two files
```
syncaudio --src "/path/to/src.flac" --dst "/path/to/dst.flac"
```

Get the offset between two Japanese tracks (ex. JPBD & USBD) and apply the offset to the English dub
```
syncaudio --src "/path/to/src.flac --dst "/path/to/dst_jpn.flac" --apply-to "/path/to/dst_eng.flac"
```


