"""Command-line interface for ProChopPy."""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from typing import Literal
from .__init__ import AnnotationReader, WaveReader, WaveWriter

__all__ = ["parse_args", "main"]

StrPath = str | Path

def parse_args() -> dict[str, str | bool]:
    _description = (
        "ProChopPy - Segment audio recordings into separate files based on ProRec annotations.\n"
        "\n"
        "ProChopPy is a Python replacement for Mark Huckvale's ProChop (part of ProRec), which "
        "chops up a recording into separate files, based on an annotation file containing the "
        "break points. ProChopPy is designed to work with files recorded using ProRec, the prompt "
        "& record program by Mark Huckvale (https://www.phon.ucl.ac.uk/resource/prorec)."
    )
    _epilog = (
        "Note: As compared to the original ProChop, ProChopPy does not implement export to the "
        "proprietary format of the Speech Filing System (SFS).\n"
        "ProChopPy also does not currently support silence detection, which ProChop supports with "
        "the -s option."
    )
    parser = ArgumentParser(
        description=_description,
        epilog=_epilog,
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("-I", action="version", version="0.1", help="Report version number and exit.")
    parser.add_argument("-a", required=True, metavar="audio.wav", help="Specify the audio file to be segmented into separate files. Can be 1 or 2 channels.")
    parser.add_argument("-t", required=True, metavar="annotations.txt", help="Specify the annotation text file containing the break points. Each line consists of a time in seconds followed by TAB and a filename label.")
    parser.add_argument("-o", required=True, metavar="output.dir", help="Specify the name of the output directory where the separate files are to be placed.")
    parser.add_argument("-f", choices=("WAV", "SFS"), default="WAV", help="Specifies the output file format. Defaults to WAV.")
    parser.add_argument("-k", action="store_true", help="Keep duplicate names. What to do if the same filename occurs more than once in the annotation file. If -k is given, duplicates are given a numbered suffix. Default is to overwrite earlier files with later ones.")
    parser.add_argument("-s", action="store_true", help="Remove silence. Attempt to identify and remove silence at the start and end of each segment.")
    arguments = parser.parse_args()
    return {
        "audio_file": arguments.a,
        "annotation_file": arguments.t,
        "output_dir": arguments.o,
        "file_type": arguments.f,
        "keep_duplicates": arguments.k,
        "remove_silence": arguments.s
    }

def main(
    audio_file: StrPath,
    annotation_file: StrPath,
    output_dir: StrPath,
    file_type: Literal["wav", "sfs"] = "wav",
    keep_duplicates: bool = False,
    remove_silence: bool = False
    ):
        # Check arguments
        audio_file = Path(audio_file)
        if not audio_file.exists() or not audio_file.is_file():
            raise FileNotFoundError(f"The audio file '{audio_file}' could not be found.")
        annotation_file = Path(annotation_file)
        if not annotation_file.exists() or not annotation_file.is_file():
            raise FileNotFoundError(f"The annotation file '{annotation_file}' could not be found.")
        output_dir = Path(output_dir)
        Path.mkdir(output_dir, parents=True, exist_ok=True)
        if not output_dir.is_dir():
            raise NotADirectoryError(f"The output directory '{output_dir}' does not exist and could not be created on the fly.")
        if file_type.lower() not in ("wav", "sfs"):
            raise ValueError(f"File type must be either 'wav' or 'sfs'; {file_type!r} specified.")

        # Read and chop
        annotations = AnnotationReader(annotation_file)
        audio_in = WaveReader(audio_file)
        audio_in_info = audio_in.get_info()
        print(audio_in.get_info())
        for start, end, label in annotations:
            output_file = output_dir / f"{label}.wav"
            audio_out = WaveWriter(output_file, audio_in_info)
            slice_data = audio_in.get_slice(start, end)
            audio_out.set_samples(slice_data)
            audio_out.close()


if __name__ == "__main__":
    arguments = parse_args()
    main(**arguments)  # type: ignore