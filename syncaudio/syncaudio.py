from subprocess import Popen, PIPE
import argparse
import os
import sys
import tempfile

from scipy import signal
from scipy.io import wavfile
import numpy as np

from pymkv import MKVFile, MKVTrack


def find_offset(file1, file2, trim, sample_rate):
    # Convert audio files to WAV and trim
    tmp1 = convert_and_trim(file1, sample_rate, trim)
    tmp2 = convert_and_trim(file2, sample_rate, trim)
    # Read WAV files
    aud1 = wavfile.read(tmp1, mmap=True)[1] / (2.0 ** 15)
    aud2 = wavfile.read(tmp2, mmap=True)[1] / (2.0 ** 15)
    # Calculate offset using cross correlation
    n = len(aud1)
    corr = signal.correlate(aud1, aud2, mode="same") / np.sqrt(
        signal.correlate(aud1, aud2, mode="same")[int(n / 2)]
        * signal.correlate(aud1, aud2, mode="same")[int(n / 2)]
    )
    delay_arr = np.linspace(-0.5 * n / sample_rate, 0.5 * n / sample_rate, n)
    delay = int(delay_arr[np.argmax(corr)] * 1000)
    # Remove temp files
    os.remove(tmp1)
    os.remove(tmp2)
    return delay


def convert_and_trim(afile, sample_rate, trim):
    tmp = tempfile.NamedTemporaryFile(mode="r+b", prefix="offset_", suffix=".wav")
    tmp_name = tmp.name
    tmp.close()
    psox = Popen(
        [
            "ffmpeg",
            "-loglevel",
            "panic",
            "-i",
            afile,
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-ss",
            "0",
            "-t",
            str(trim),
            "-acodec",
            "pcm_s16le",
            tmp_name,
        ],
        stderr=PIPE,
    )
    psox.communicate()
    if psox.returncode != 0:
        raise Exception("FFMpeg failed")
    return tmp_name


def mux_file(file, offset):
    # Set output file name
    basename = os.path.splitext(file)[0]
    output = os.path.join(basename + " [{}ms].mka").format(str(offset))
    # Create mka file
    track = MKVTrack(file)
    track.default_track = True
    track.sync = offset
    mka = MKVFile()
    mka.add_track(track)
    mka.mux(output)


def main():
    parser = argparse.ArgumentParser(
        description="Find offset between two audio tracks and sync them"
    )
    parser.add_argument(
        "--src",
        required=True,
        dest="source_file",
        metavar="<filename>",
        help="""
    Audio file that has desired sync""",
    )
    parser.add_argument(
        "--dst",
        required=True,
        dest="dest_file",
        metavar="<filename>",
        help="""
    Audio file to be synced""",
    )
    parser.add_argument(
        "--apply-to",
        dest="apply_to",
        metavar="<filename>",
        help="""
    File to apply offset to""",
    )
    parser.add_argument(
        "--trim",
        dest="trim",
        default=900,
        type=int,
        metavar="<seconds>",
        help="""
    Only uses first n seconds of audio files [%(default)s]""",
    )
    parser.add_argument(
        "--sample-rate",
        default=8000,
        type=int,
        metavar="<rate>",
        dest="sample_rate",
        help="Target sample rate during downsampling [%(default)s]",
    )
    args = parser.parse_args()

    # Get the offset
    offset = find_offset(
        args.source_file, args.dest_file, args.trim, args.sample_rate
    )
    print("Offset is " + str(offset) + "ms")

    # Mux file with delay
    if args.apply_to:
        mux_file(args.apply_to, offset)
    else:
        mux_file(args.dest_file, offset)


if __name__ == "__main__":
    sys.exit(main())
