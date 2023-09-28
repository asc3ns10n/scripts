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
    """
    Find the offset between two audio files using cross-correlation.
    
    Parameters:
    - file1, file2: Paths to the two audio files to be compared.
    - trim: Duration for trimming the audio.
    - sample_rate: Sample rate to be used for the audio files.
    
    Returns:
    - delay: Offset in milliseconds between the two audio files.
    """
    
    tmp1 = convert_and_trim(file1, sample_rate, trim)
    tmp2 = convert_and_trim(file2, sample_rate, trim)
    
    aud1 = wavfile.read(tmp1, mmap=True)[1] / (2.0 ** 15)
    aud2 = wavfile.read(tmp2, mmap=True)[1] / (2.0 ** 15)
    
    n = len(aud1)
    correlation = signal.correlate(aud1, aud2, mode="same")
    corr_normalization = correlation[int(n / 2)] * correlation[int(n / 2)]
    
    corr = correlation / np.sqrt(corr_normalization)
    
    delay_arr = np.linspace(-0.5 * n / sample_rate, 0.5 * n / sample_rate, n)
    delay = int(delay_arr[np.argmax(corr)] * 1000)

    os.remove(tmp1)
    os.remove(tmp2)

    return delay


def convert_and_trim(audio_file, sample_rate, trim_duration):
    """
    Convert an audio file to a specified sample rate and trim its duration.

    Parameters:
    - audio_file: Path to the input audio file.
    - sample_rate: Desired sample rate for the output.
    - trim_duration: Duration to which the audio should be trimmed.

    Returns:
    - tmp_name: Path to the converted and trimmed temporary WAV file.
    """
    
    with tempfile.NamedTemporaryFile(mode="r+b", prefix="offset_", suffix=".wav", delete=False) as tmp:
        tmp_name = tmp.name

        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel", "panic",
            "-i", audio_file,
            "-ac", "1",
            "-ar", str(sample_rate),
            "-ss", "0",
            "-t", str(trim_duration),
            "-acodec", "pcm_s16le",
            tmp_name
        ]

        process = Popen(ffmpeg_cmd, stderr=PIPE)
        _, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f"FFMpeg failed with error: {stderr.decode('utf-8')}")

    return tmp_name


def mux_file(file_path, offset):
    """
    Create a Matroska audio (.mka) file with a specified offset.

    Parameters:
    - file_path: Path to the input audio file.
    - offset: Offset value in milliseconds.

    Side Effect:
    - Produces an .mka file with the specified offset.
    """
    
    if not os.path.exists(file_path):
        raise ValueError(f"The file '{file_path}' does not exist.")
    
    basename = os.path.splitext(file_path)[0]
    output = f"{basename} [{offset}ms].mka"

    track = MKVTrack(file_path)
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

    if not os.path.exists(args.source_file):
        print(f"Error: Source file '{args.source_file}' does not exist.", file=sys.stderr)
        return 1
    if not os.path.exists(args.dest_file):
        print(f"Error: Destination file '{args.dest_file}' does not exist.", file=sys.stderr)
        return 1

    try:
        offset = find_offset(args.source_file, args.dest_file, args.trim, args.sample_rate)
        print(f"Offset is {offset}ms")
        mux_file(args.apply_to if args.apply_to else args.dest_file, offset)
        return 0  # Successful execution
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1  # Indicate an error


if __name__ == "__main__":
    sys.exit(main())
