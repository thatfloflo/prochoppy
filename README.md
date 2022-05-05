# ProChopPy

ProChopPy - Segment audio recordings into separate files based on ProRec annotations.

ProChopPy is a Python replacement for Mark Huckvale's ProChop (part of ProRec), which chops up a recording into separate files, based on an annotation file containing the break points. ProChopPy is designed to work with files recorded using ProRec, the prompt & record program by Mark Huckvale (https://www.phon.ucl.ac.uk/resource/prorec).

## Usage
`python -m prochoppy [-h] [-I] -a audio.wav -t annotations.txt -o output.dir [-f {WAV,SFS}] [-k] [-s]`

## Options
| Option         | Parameters      | Description                              |
|----------------|-----------------|------------------------------------------|
| `-h`           |                 | Show help message and exit.              |
| `-I`           |                 | Report version number and exit.          |
| `-a`           | audio.wav       | Specify the audio file to be segmented into separate files. Can be 1 or 2 channels.
| `-t`           | annotations.txt |  Specify the annotation text file containing the break points. Each line consists of a time in seconds followed by TAB and a filename label. |
| `-o`           | output.dir      | Specify the name of the output directory where the separate files are to be placed. |
| `-f`           | {WAV,SFS}       | Specifies the output file format. Defaults to WAV. |
| `-k`           |                 | Keep duplicate names. What to do if the same filename occurs more than once in the annotation file. If -k is given, duplicates are given a numbered suffix. Default is to overwrite earlier files with later ones. |
| `-s`           |                 | Remove silence. Attempt to identify and remove silence at the start and end of each segment. |

## Note
As compared to the original ProChop, ProChopPy does not implement export to the proprietary format of the Speech Filing System (SFS).
ProChopPy also does not currently support silence detection, which ProChop supports with the -s option.
