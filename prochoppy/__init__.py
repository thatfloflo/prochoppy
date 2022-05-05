"""Package init file for ProChopPy."""
from copy import copy
from wave import open as wave_open, Wave_read, Wave_write
from pathlib import Path
from typing import NamedTuple

__all__ = ["AnnotationReader", "WaveInfo", "WaveReader", "WaveWriter"]

StrPath = str | Path


class WaveInfo(NamedTuple):
    """Class to represent information about a wave audio object.

    The named tuple has the following keys:
        - n_channels: Number of audio channels.
        - sample_width: The sample width in bytes.
        - sample_rate: The sampling frequency.
        - n_samples: The number of audio frames.
        - compression_type: The compression type (always 'NONE').
        - compression_name: A human-readable version of the compression_type,
            e.g. 'not compressed'.
        - length: Length of recording in seconds ()= n_samples / sample_rate).
    """
    n_channels: int = 1
    sample_width: int = 1
    sample_rate: int = 44100
    n_samples: int = 0
    compression_type: str = "NONE"
    compression_name: str = "not compressed"

    @property
    def length(self) -> float:
        """Returns the wave audio length in seconds (float)."""
        return self.n_samples / self.sample_rate


class AnnotationReader:
    """Class for reading ProRec annotation files."""

    _filename: Path
    _markers: list[tuple[float, str]]
    _sections: list[tuple[float, float, str]]
    _max_marker_len: int

    def __init__(self, filename: StrPath):
        self._markers = []
        self._sections = []
        self._max_marker_len = 0
        self._filename = Path(filename)
        if not self._filename.exists():
            raise FileNotFoundError(f"File '{filename}' does not exist.")
        self._read()
        self._compute_sections()

    def _read(self):
        with self._filename.open("r") as fp:
            for line in fp:
                if "\t" not in line:
                    raise IOError("File appears not to be a valid ProRec annotation file.")
                time, label = line.split("\t", maxsplit=2)
                self._markers.append((float(time), label.strip()))
                self._max_marker_len = max(self._max_marker_len, len(label.strip()))
    
    def _compute_sections(self):
        max = len(self._markers)
        for i in range(max):
            start_time, label = self._markers[i]
            if i + 1 < max:
                end_time = self._markers[i + 1][0]
                self._sections.append((start_time, end_time, label))

    def get_markers(self) -> dict[float, str]:
        """Get a copy of the Annotation markers."""
        return copy(self._markers)  # type: ignore

    def get_max_marker_len(self) -> int:
        """Get the maximal length of a marker label."""
        return self._max_marker_len

    def get_filename(self) -> Path:
        """Get the filename of the annotation file."""
        return self._filename

    def __iter__(self):
        return copy(self._sections).__iter__()

    def __len__(self):
        return len(self._sections)


class WaveReader:
    """Class for reading wave files."""

    _filename: Path
    _fp: Wave_read
    _info: WaveInfo

    def __init__(self, filename: StrPath):
        self._filename = Path(filename)
        self._fp: Wave_read = wave_open(str(filename), mode="rb")
        self._info = WaveInfo(
            n_channels=self._fp.getnchannels(),
            sample_width=self._fp.getsampwidth(),
            sample_rate=self._fp.getframerate(),
            n_samples=self._fp.getnframes(),
            compression_type=self._fp.getcomptype(),
            compression_name=self._fp.getcompname()
        )

    def get_filename(self):
        """Returns the filename of the wave file."""
        return copy(self._filename)

    def get_info(self) -> WaveInfo:
        """Returns a dictionary with file information."""
        return copy(self._info)

    def get_slice(self, start_seconds: float, end_seconds: float) -> bytes:
        """Return bytes between two points, specified in seconds (float)."""
        if start_seconds >= end_seconds:
            raise ValueError("Start time must be before end time.")
        start_sample = int(start_seconds * self._info.sample_rate)
        end_sample = int(end_seconds * self._info.sample_rate)
        self._fp.rewind()
        self._fp.readframes(start_sample - 1) # use to advance to correct frame, discard data
        return self._fp.readframes(end_sample - start_sample)

    def close(self):
        self._fp.close()

    def __del__(self):
        self.close()


class WaveWriter:

    _filename: Path
    _fp: Wave_write
    _info: WaveInfo

    def __init__(self, filename: StrPath, settings: WaveInfo):
        self._filename = Path(filename)
        self._fp: Wave_write = wave_open(str(filename), "wb")
        self._fp.setnchannels(settings.n_channels)
        self._fp.setsampwidth(settings.sample_width)
        self._fp.setframerate(settings.sample_rate)
        self._fp.setcomptype(settings.compression_type, settings.compression_name)
    
    @property
    def info(self):
        return WaveInfo(
            n_channels=self._fp.getnchannels(),
            sample_width=self._fp.getsampwidth(),
            sample_rate=self._fp.getframerate(),
            n_samples=self._fp.getnframes(),
            compression_type=self._fp.getcomptype(),
            compression_name=self._fp.getcompname()
        )

    def get_filename(self):
        """Returns the filename of the wave file."""
        return copy(self._filename)

    def get_info(self) -> WaveInfo:
        """Returns a dictionary with file information.
        
        The dictionary has the following keys:
            - n_channels: Number of audio channels.
            - sample_width: The sample width in bytes.
            - sample_rate: The sampling frequency.
            - n_samples: The number of audio frames.
            - compression_type: The compression type (always 'NONE').
            - compression_name: A human-readable version of the compression_type,
                e.g. 'not compressed'.
        """
        return copy(self._info)

    def set_samples(self, data: bytes):
        self._fp.writeframes(data)

    def close(self):
        self._fp.close()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    print("To directly invoke ProChopPy, run python -m prochoppy [options].")