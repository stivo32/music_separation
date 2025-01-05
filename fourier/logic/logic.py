from enum import Enum
from pathlib import Path
from spleeter.separator import Separator
from pydub import AudioSegment

output = Path('../../output')

song = 'The Rasmus - In the Shadows (Official Music Video).mp3'
song = 'Queen - The Show Must Go On (Official Video).mp3'


class SongParts(Enum):
    bass = 'bass.wav'
    drums = 'drums.wav'
    vocals = 'vocals.wav'
    other = 'other.wav'


class SplitType(Enum):
    five_stems = '5stems'  # vocal + bass + drums + piano + other
    two_stems = '2stems'  # vocal and other
    four_stems = '4stems'  # vocal + bass + drums + other


def convert_to_mp3(path: Path):
    pass


def split_by_spleeter(path_to_file: Path, split_type: SplitType):
    separator = Separator(f'spleeter:{split_type.value}')

    separator.separate_to_file(str(path_to_file), str(output / 'spleeter' / split_type.value) )


def noise_reduction(path_to_file):
    pass


def combine_together(song_name: str, *paths: Path):
    parts = []
    for path in paths:
        parts.append(AudioSegment.from_file(str(path)))

    melody = parts.pop(0)
    for part in parts:
        melody = melody.overlay(part)

    melody.export(f'{song_name}.wav', format='wav')


def main():
    music = Path('../..') / song
    print(music.is_file())
    split_type = SplitType.four_stems
    # split_by_spleeter(music, split_type)

    paths = [
        Path('../../output/spleeter') / split_type.value / song.rsplit('.', maxsplit=1)[0] / part.value for part in [
            SongParts.vocals,
            SongParts.bass,
            SongParts.drums,
            # SongParts.other,
        ]
    ]

    combine_together(song, *paths)


if __name__ == "__main__":
    main()
