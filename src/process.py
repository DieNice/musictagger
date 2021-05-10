import glob

from src.tag import MyMp3
from src.rename import TagDictBuilderAbstract, TagDict, FileHandler, FileWriter, BatchRename
from typing import Tuple, List


def build_tags(tagFile: str, builder: TagDictBuilderAbstract, album: str, disc: str):
    lines = open(tagFile, "r").readlines()

    tags = []
    for line in lines:
        result = builder.build(line)
        result.setAlbum(album)
        result.setDisc(disc)
        tags.append(result)
    return tags


def new_build_tags(records: List[Tuple[str, str, str, str, str, str, str]], builder: TagDictBuilderAbstract):
    tags = []
    for record in records:
        result = builder.build(record)
        tags.append(result)
    return tags


def build_files(musicFolder: str) -> List[MyMp3]:
    ''':return mp3 files from direcotry or files paths'''
    files = glob.glob(musicFolder + "/*.mp3")
    mp3s = []
    for file in files:
        mp3s.append(MyMp3(file))
    return mp3s


def new_build_fiels(records: List[Tuple[str, str, str, str, str, str, str]]) -> List[MyMp3]:
    ''':return mp3 files from direcotry or files paths'''
    mp3s = []
    for file in records:
        mp3s.append(MyMp3(file[-1]))
    return mp3s


def build_files_from_table() -> List[MyMp3]:
    pass


def getTagsTromTable() -> List[str]:
    pass


def process(tags: List[TagDict], mp3s: List[MyMp3], baseDir: str, schema: str) -> None:
    batch = BatchRename(tags, mp3s)
    batch.tagAll()
    fh = FileHandler()
    fileCollectionWriter = FileWriter(baseDir, schema, fh)
    for mp3 in mp3s:
        fileCollectionWriter.copy(mp3, True)
