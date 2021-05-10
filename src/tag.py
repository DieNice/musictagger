from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TPOS, TRDA
import mutagen.id3
import mutagen
from typing import Dict

ARTIST = "Artist"
ALBUM = "Album"
TITLE = "Title"
TRACK = "Track"
YEAR = "Year"
DISC = "Disc"
KNOWN_TAGS = [ARTIST, ALBUM, TITLE, TRACK, YEAR, DISC]

class TagFile:
    '''Class tag of mp3 file'''

    def tags(self) -> Dict:
        ''':return dict of tags'''
        return {ARTIST: [self.artist, self.set_artist], ALBUM: [self.album, self.set_album],
                TRACK: [self.track, self.set_track], TITLE: [self.title, self.set_title],
                DISC: [self.disc, self.set_disc], YEAR: [self.year, self.set_year]}

    def set_tag(self, tag: str, value: str) -> None:
        self.tags()[tag][1](value)

    def get_tag(self, tag: str) -> None:
        return self.tags()[tag][0]()

    def artist(self) -> str:
        return self._read(ARTIST)

    def set_artist(self, artist: str) -> None:
        self._write(ARTIST, artist)

    def title(self) -> str:
        return self._read(TITLE)

    def set_title(self, title: str) -> str:
        self._write(TITLE, title)

    def album(self) -> str:
        return self._read(ALBUM)

    def set_album(self, album: str) -> None:
        self._write(ALBUM, album)

    def track(self) -> str:
        return self._read(TRACK)

    def set_track(self, track: str) -> None:
        self._write(TRACK, track)

    def disc(self) -> str:
        return self._read(DISC)

    def set_disc(self, disc: str) -> None:
        self._write(DISC, disc)

    def year(self) -> str:
        return self._read(YEAR)

    def set_year(self, year: str) -> None:
        self._write(YEAR, year)

    def save(self) -> None:
        self.file.save()

        
class MyMp3(TagFile):
    '''Class meta mp3 file contains tags'''
    writeDict = {ARTIST: TPE1, ALBUM: TALB, TRACK: TRCK, TITLE: TIT2, DISC: TPOS, YEAR: TRDA}
    readDict = {ARTIST: "TPE1", ALBUM: "TALB", TRACK: "TRCK", TITLE: "TIT2", DISC: "TPOS", YEAR: "TRDA"}

    def __init__(self, fname: str) -> None:
        self.extension = "mp3"
        self.fname = fname
        try:
            self.file = ID3(fname)
        except mutagen.id3.ID3NoHeaderError:
            sub_file = mutagen.File(fname)
            sub_file.add_tags()
            sub_file.save(fname)
            self.file = sub_file.tags

    def _read(self, tag: str) -> str:
        ''':return tag from mp3 file'''
        try:
            return self.file.get(MyMp3.readDict[tag]).text[0]
        except AttributeError:
            return ""

    def _write(self, tag: str, value: str) -> None:
        '''add tag to mp3 file'''
        self.file.add(MyMp3.writeDict[tag](encoding=0, text=value))