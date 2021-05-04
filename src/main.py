import glob
import os, sys
import PyQt5

from rename import TagDictBuilder, TagDict, FileHandler, FileWriter, BatchRename
from tag import MyMp3
from typing import List
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QUrl, QPoint
from PyQt5 import QtGui, QtWidgets
from PIL import Image
from gui import design
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL.ImageQt import ImageQt


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    FILEPATH = 6

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.actionOpen_files.triggered.connect(self.load_files_mp3)
        self.actionExit.triggered.connect(self.exit)
        self.tableWidget.cellClicked.connect(self.select_row)
        self.addButton.clicked.connect(self.load_file_mp3)
        self.deleteButton.clicked.connect(self.delete_selected_rows)
        self.__center()
        self.__setAligmentTableColumns()

    def __center(self):
        frameGm = self.frameGeometry()
        screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(
            PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def __setAligmentTableColumns(self):
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)

    def exit(self):
        exit()

    def load_files_mp3(self):
        urls = QFileDialog.getOpenFileUrls(self, 'Open mp3 files', filter='*.mp3')
        return self.load_urls_to_table(urls[0])

    def load_file_mp3(self):
        urls = QFileDialog.getOpenFileUrl(self, 'Open mp3 file', filter='*.mp3')
        return self.load_urls_to_table([urls[0]])

    def load_picto(self, url):
        '''load picture from data mp3 to label or set default image'''
        tags = ID3(url)
        try:
            pict = tags.get("APIC:").data
            im = Image.open(BytesIO(pict))
            qim = ImageQt(im)
            pix = QtGui.QPixmap.fromImage(qim)
            pix.detach()
            self.label_image.setPixmap(pix)
        except Exception:
            self.label_image.setPixmap(QtGui.QPixmap(":/pictures/empty_logo.jpg"))

    def load_urls_to_table(self, urls: List[QUrl]):
        table = self.tableWidget
        for item in urls:
            mp3 = readFile(item.path())
            row = table.rowCount()
            table.setRowCount(row + 1)
            mp3 = readFile(item.path())
            name = QTableWidgetItem(str(item.fileName()))
            table.setItem(row, 0, name)

            title = QTableWidgetItem(str(mp3.title()))
            table.setItem(row, 1, title)

            artist = QTableWidgetItem(str(mp3.artist()))
            table.setItem(row, 2, artist)

            album = QTableWidgetItem(str(mp3.album()))
            table.setItem(row, 3, album)

            disc = QTableWidgetItem(str(mp3.disc()))
            table.setItem(row, 4, disc)

            track = QTableWidgetItem(str(mp3.track()))
            table.setItem(row, 5, track)

            filepath = QTableWidgetItem(str(item.path()))
            table.setItem(row, 6, filepath)
            self.tableWidget.resizeColumnsToContents()

    def select_row(self):
        index = self.tableWidget.selectedIndexes()[-1].row()
        print(index)
        self.load_picto(self.tableWidget.item(index, self.FILEPATH).text())
        self.setDescriptionMp3(index)

    def delete_selected_rows(self) -> None:
        count = len([index.row() for index in self.tableWidget.selectedIndexes()])
        for _ in range(count):
            index = self.tableWidget.selectedIndexes()[0].row()
            self.tableWidget.removeRow(index)

    def setDescriptionMp3(self, indexrow: int) -> None:
        filepath = self.tableWidget.item(indexrow, self.FILEPATH).text()
        file = MP3(filepath)
        filename = file.filename.split('/')[-1]
        desc = f"filename:{filename}\nfilepath:{file.filename}\nlength:{file.info.length} seconds\nchannels:{str(file.info.channels)}\nbitrate:{str(file.info.bitrate)}"
        self.label_description_music.setText(desc)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


def buildTags(tagFile: str, builder: TagDictBuilder, album: str, disc: str):
    lines = open(tagFile, "r").readlines()

    tags = []
    for line in lines:
        result = builder.build(line)
        result.setAlbum(album)
        result.setDisc(disc)
        tags.append(result)
    return tags


def buildFiles(musicFolder: str) -> List[MyMp3]:
    ''':return mp3 files from direcotry or files paths'''
    files = glob.glob(musicFolder + "/*.mp3")
    mp3s = []
    for file in files:
        mp3s.append(MyMp3(file))
    return mp3s


def buildFilesFromTable() -> List[MyMp3]:
    pass


def readFile(path: str):
    ''':return tag mp3file'''
    return MyMp3(path)


def uniteAlbums() -> List[str]:
    '''Unite traks from table by album'''
    pass


def getTagsTromTable() -> List[str]:
    pass


def proces(tags: List[TagDict], mp3s: List[MyMp3], baseDir: str, schema: str) -> None:
    batch = BatchRename(tags, mp3s)
    batch.tagAll()
    fh = FileHandler()
    fileCollectionWriter = FileWriter(baseDir, schema, fh)
    for mp3 in mp3s:
        fileCollectionWriter.copy(mp3, True)


if __name__ == '__main__':
    main()
    # builder = TagDictBuilder("%track. %title - %artist")
    # tagFile1 = "/home/pda/Projects/PycharmProjects/mymusictagger/tagfile"
    # musicFolder1 = "/home/pda/Projects/PycharmProjects/mymusictagger/musiconefile"
    # baseDir = "/home/pda/Projects/PycharmProjects/mymusictagger/"
    # schema = "%album (disc %disc)/%track - %artist - %title"
    #
    # tags = buildTags(tagFile1, builder, "Album name", "first")
    # mp3s = buildFiles(musicFolder1)
    # proces(tags, mp3s, baseDir, schema)
