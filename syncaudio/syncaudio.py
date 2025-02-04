from subprocess import Popen, PIPE
import argparse
import os
import sys
import tempfile
from typing import Optional, Generator, List
from contextlib import contextmanager

from scipy import signal
from scipy.io import wavfile
import numpy as np

from pymkv2 import MKVFile, MKVTrack
from pydub import AudioSegment


@contextmanager
def temporary_wav_files() -> Generator[List[str], None, None]:
    """Context manager for handling temporary WAV files."""
    temp_files = []
    try:
        yield temp_files
    finally:
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except OSError:
                pass


def find_offset(file1: str, file2: str, trim: int, sample_rate: int) -> int:
    """
    Find the offset between two audio files using cross-correlation.
    
    Parameters:
    - file1, file2: Paths to the two audio files to be compared.
    - trim: Duration for trimming the audio.
    - sample_rate: Sample rate to be used for the audio files.
    
    Returns:
    - delay: Offset in milliseconds between the two audio files.
    
    Raises:
    - ValueError: If input parameters are invalid
    """
    if not all(os.path.exists(f) for f in [file1, file2]):
        raise ValueError("Both audio files must exist")
    if trim <= 0:
        raise ValueError("Trim duration must be positive")
    if sample_rate <= 0:
        raise ValueError("Sample rate must be positive")
        
    with temporary_wav_files() as temp_files:
        tmp1 = convert_and_trim(file1, sample_rate, trim)
        tmp2 = convert_and_trim(file2, sample_rate, trim)
        temp_files.extend([tmp1, tmp2])
        
        aud1 = wavfile.read(tmp1, mmap=True)[1] / (2.0 ** 15)
        aud2 = wavfile.read(tmp2, mmap=True)[1] / (2.0 ** 15)
        
        n = len(aud1)
        correlation = signal.correlate(aud1, aud2, mode="same")
        corr_normalization = correlation[int(n / 2)] * correlation[int(n / 2)]
        
        corr = correlation / np.sqrt(corr_normalization)
        
        delay_arr = np.linspace(-0.5 * n / sample_rate, 0.5 * n / sample_rate, n)
        delay = int(delay_arr[np.argmax(corr)] * 1000)

    return delay


def convert_and_trim(audio_file: str, sample_rate: int, trim_duration: int) -> str:
    """
    Convert an audio file to a specified sample rate and trim its duration.

    Parameters:
    - audio_file: Path to the input audio file.
    - sample_rate: Desired sample rate for the output.
    - trim_duration: Duration to which the audio should be trimmed.

    Returns:
    - tmp_name: Path to the converted and trimmed temporary WAV file.
    """
    print(f"Converting {os.path.basename(audio_file)}...", file=sys.stderr)
    
    with tempfile.NamedTemporaryFile(mode="w+b", prefix="offset_", suffix=".wav", delete=False) as tmp:
        tmp_name = tmp.name
        
        # Load audio and convert to mono
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1)
        
        # Set sample rate
        audio = audio.set_frame_rate(sample_rate)
        
        # Trim duration (pydub works in milliseconds)
        trim_ms = trim_duration * 1000
        audio = audio[:trim_ms]
        
        # Export as WAV
        audio.export(tmp_name, format="wav", parameters=["-acodec", "pcm_s16le"])

    return tmp_name


def mux_file(file_path: str, offset: int) -> None:
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

    if os.path.exists(output):
        response = input(f"Output file '{output}' already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return
    
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
    Only uses first n seconds of audio files [%(default)s]"""
    )
    parser.add_argument(
        "--sample-rate",
        default=8000,
        type=int,
        metavar="<rate>",
        dest="sample_rate",
        help="""
    Target sample rate during downsampling [%(default)s]"""
    )
    parser.add_argument(
        "--display-only",
        action="store_true",
        help="""
    If set, the offset will only be displayed and not applied"""
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
        if not args.display_only:
            mux_file(args.apply_to if args.apply_to else args.dest_file, offset)
        return 0  # Successful execution
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1  # Indicate an error


if __name__ == "__main__":
    sys.exit(main())
