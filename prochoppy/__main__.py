"""Command-line interface for ProChopPy."""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from typing import Literal
from . import AnnotationReader, WaveReader, WaveWriter, cliutil as cli

__all__ = ["parse_args", "main"]

StrPath = str | Path

def parse_args() -> dict[str, str | bool]:
    _description = cli.convert(
        "<s bright><f green>ProChopPy</f> - Segment audio recordings into separate files based "
        "on ProRec annotations.</s><br>"
        "<br>"
        "ProChopPy is a Python replacement for Mark Huckvale's ProChop (part of ProRec), which "
        "chops up a recording into separate files, based on an annotation file containing the "
        "break points. ProChopPy is designed to work with files recorded using ProRec, the prompt "
        "&amp; record program by Mark Huckvale (https://www.phon.ucl.ac.uk/resource/prorec)."
    )
    _epilog = cli.convert(
        "Note: <s dim>As compared to the original ProChop, ProChopPy does not implement export to the "
        "proprietary format of the Speech Filing System (SFS).<br>\n"
        "ProChopPy also does not currently support silence detection, which ProChop supports with "
        "the -s option.</s>"
    )
    parser = ArgumentParser(
        description=_description,
        epilog=_epilog,
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("-I", action="version", version="0.1.1", help="Report version number and exit.")
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
        cli.writeln("<s bright><f yellow>Chopping audio file with ProChopPy...</f></s>")
        annotations = AnnotationReader(annotation_file)
        cli.writeln(f"<s dim>Annotation file:   <f green>{annotations.get_filename()}</f></s>")
        cli.writeln(f"<s dim>  - Sections:      <f cyan>{len(annotations)}</f></s>")
        audio_in = WaveReader(audio_file)
        audio_in_info = audio_in.get_info()
        cli.writeln(f"<s dim>Source audio file: <f green>{audio_in.get_filename()}</f></s>")
        cli.writeln(f"<s dim>  - Channels:      <f cyan>{audio_in_info.n_channels}</f></s>")
        cli.writeln(f"<s dim>  - Sample rate:   <f cyan>{audio_in_info.sample_rate}Hz</f></s>")
        cli.writeln(f"<s dim>  - Length:        <f cyan>{audio_in_info.length}s</f></s>")
        cli.writeln(f"<s dim>Output directory:  <f green>{output_dir}</f></s>")
        counter: int = 1
        max: int = len(annotations)
        counter_width: int = len(str(max))
        label_width: int = annotations.get_max_marker_len()
        for start, end, label in annotations:
            if counter > 1:
                cli.clearln()
            cli.write(f"<s bright>Processing files:</s>  ")
            cli.write(f"<s dim><f cyan>{str(counter).rjust(counter_width)}/{max}</f></s> ")
            cli.write(f"<f green>{label.ljust(label_width)} </f><s dim><f cyan>({start}s to {end}s)</f></s>")
            output_file = output_dir / f"{label}.wav"
            audio_out = WaveWriter(output_file, audio_in_info)
            slice_data = audio_in.get_slice(start, end)
            audio_out.set_samples(slice_data)
            audio_out.close()
            counter += 1
        cli.newln()
        cli.writeln(f"<s bright><f yellow>Chopping completed.</f></s>")


if __name__ == "__main__":
    cli.init()
    arguments = parse_args()
    main(**arguments)  # type: ignore