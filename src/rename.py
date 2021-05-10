from __future__ import annotations
import glob
import src.tag as tag
import re
import shutil
import os
from abc import ABC, abstractmethod, abstractproperty
from src.tag import KNOWN_TAGS
from src.tag import MyMp3
from typing import List, Dict

TRACK = "%track"
TITLE = "%title"
ALBUM = "%album"
DISC = "%disc"
ARTIST = "%artist"
YEAR = "%year"
TAGDICT = {TRACK: tag.TRACK, TITLE: tag.TITLE, ALBUM: tag.ALBUM, ARTIST: tag.ARTIST, DISC: tag.DISC, YEAR: tag.YEAR}


class TagDict:
    '''Class contains dictionary of tags'''

    def __init__(self, dict: Dict) -> None:
        self.dict = dict

    def keys(self):
        return self.dict.keys()

    def items(self):
        return self.dict.items()

    def values(self):
        return self.dict.values()

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, item):
        if key not in KNOWN_TAGS:
            raise KeyError
        self.dict[key] = item

    def __contains__(self, key):
        return self.dict.__contains__(key)

    def __iter__(self):
        return self.dict.__iter__()

    def setAlbum(self, album: str) -> None:
        self[TAGDICT[ALBUM]] = album

    def setTitle(self, title: str) -> None:
        self[TAGDICT[TITLE]] = title

    def setTrack(self, track: str) -> None:
        self[TAGDICT[TRACK]] = track

    def setDisc(self, disc: str) -> None:
        self[TAGDICT[DISC]] = disc

    def setArtist(self, artist: str) -> None:
        self[TAGDICT[ARTIST]] = artist


class TagDictBuilderAbstract(ABC):
    ITEMS = []

    def __init__(self):
        pass

    @abstractmethod
    def build(record) -> TagDict:
        pass


class TagDictBuilderLine(TagDictBuilderAbstract):
    '''Class for buildings dictionary of tags for mp3 file'''
    ITEMS = [TRACK, TITLE, ALBUM, ARTIST, YEAR]
    REGEX = re.compile("(" + TRACK + ")|(" + TITLE + ")|(" + ALBUM + ")|(" + ARTIST + ")|(" + DISC + ")|(" + YEAR + ")")

    def __init__(self, regex: str) -> None:
        super(TagDictBuilderLine, self).__init__()
        self.regex = TagDictBuilderLine._buildRegex(regex)

    def build(self, line: str) -> TagDict:
        '''Building dictonary of tagsfor mp3'''
        filtered = self.regex
        currentMatch = ""
        result = {}
        for match in filtered:
            if match in TagDictBuilderLine.ITEMS:
                currentMatch = match
            else:
                print(line)
                print("eat: " + match)
                eaten = self._eat(line, match)
                line = eaten[1]
                if currentMatch != "":
                    print(currentMatch)
                    print(eaten)
                    result[TAGDICT[currentMatch]] = eaten[0].strip()
            filtered = filtered[1:]
        return TagDict(result)

    def _eat(self, line: str, token: str) -> List[str]:
        '''Parsing line by token match'''
        token = re.escape(token)
        result = re.split("(" + token + ")", line, 1)
        result = [k for k in result if k != ""]
        return [result[0], result[-1]]

    def _buildRegex(regex: str) -> List[str]:
        '''Building regex list'''
        splitted = TagDictBuilderLine.REGEX.split(regex)
        return [k for k in splitted if k != None]


class TagDictBuilderRecord(TagDictBuilderAbstract):
    ITEMS = [TRACK, TITLE, ARTIST, ALBUM, DISC, YEAR]

    def build(self, record) -> TagDict:
        result = {}
        index = 0
        for item in self.ITEMS:
            result[TAGDICT[item]] = record[index]
            index += 1
        return TagDict(result)


class TagWriter:
    '''Class for writing tags to mp3 file'''

    def __init__(self, file: MyMp3) -> None:
        self.file = file

    def writeTags(self, tagDict: TagDict) -> None:
        for tag in tagDict:
            self.file.set_tag(tag, tagDict[tag])

    def save(self) -> None:
        self.file.save()


class FileWriter:
    '''Class for writing mp3 file to dirs by schema'''

    def __init__(self, path: str, schema: str, fileHandler: FileHandler) -> None:
        self.schema = schema
        self.path = path
        self.fh = fileHandler

    def move(self, file: MyMp3) -> None:
        self.move(file, False)

    def move(self, file: MyMp3, overwrite: bool) -> None:
        src = self._getSource()
        dst = self._getDestination()
        self.fh.move(src, dst, overwrite)

    def copy(self, file: MyMp3, overwrite: bool = False) -> None:
        src = self._getSource(file)
        dst = self._getDestination(file)
        self.fh.copy(src, dst, overwrite)

    def _getSource(self, file: MyMp3) -> str:
        return file.fname

    def _getDestination(self, file: MyMp3) -> str:
        return os.path.join(self.path, self._translateSchema(file)) + "." + file.extension

    def _translateSchema(self, file: MyMp3) -> str:
        '''Translation schema for moving mp3 file to new folders'''
        location = self.schema
        for tag in TAGDICT:
            location = location.replace(tag, file.get_tag(TAGDICT[tag]))
        return location


class FileHandler:
    '''Class for working with files'''

    def copy(self, src: str, dst: str, overwrite: bool) -> None:
        if overwrite == False and self._exists(dst):
            print(dst + ": exists")
        self.ensure_dir(dst)
        shutil.copy2(src, dst)

    def move(self, src: str, dst: str, overwrite: bool) -> None:
        if overwrite == False and self._exists(dst):
            raise IOError(dst + ": exists")
        self.ensure_dir(dst)
        shutil.move(src, dst)

    def _exists(self, path: str) -> bool:
        return os.path.exists(path)

    def ensure_dir(self, f: str) -> None:
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)


class BatchRename:
    '''Class packet for rename'''

    def __init__(self, tagDicts: List[TagDict], musicFiles: List[MyMp3]) -> None:
        self.tagDicts = tagDicts
        self.musicFiles = musicFiles

    def tagAll(self) -> None:
        '''Add new tages for batch'''
        for (file, tagDict) in zip(self.musicFiles, self.tagDicts):
            tw = TagWriter(file)
            tw.writeTags(tagDict)
            tw.save()
