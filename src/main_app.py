import sys
from time import sleep
from typing import Tuple, List
import PyQt5
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QUrl, Qt
from PyQt5 import QtGui, QtWidgets
from PIL import Image
from gui import design
from src.tag import MyMp3
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL.ImageQt import ImageQt
from src.rename import TagDictBuilderRecord
from PyQt5.QtWidgets import QMessageBox
from src.process import new_build_fiels, new_build_tags, process


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    '''Class of gui app'''
    FILEPATH = 6
    schems = ["%album /%track - %artist - %title", "%artist %album/%track - %artist - %title"]

    schems_numfields = {0: 3, 1: 2}

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.actionOpen_files.triggered.connect(self.__load_files_mp3)
        self.addButton.clicked.connect(self.__load_file_mp3)
        self.actionExit.triggered.connect(self.__exit_from_app)
        self.tableWidget.cellClicked.connect(self.__select_row)
        self.actionSave_files_to.triggered.connect(self.__save_file_to)
        self.deleteButton.clicked.connect(self.__delete_selected_rows)
        self.pathButton.clicked.connect(self.__load_path_directory_to_save)
        self.processButton.clicked.connect(self.__process)
        self.actionAbout.triggered.connect(self.__show_about)
        self.actionHelp.triggered.connect(self.__show_help)
        self.__center()
        self.__setAligmentTableColumns()
        self.builder = TagDictBuilderRecord()

    def __show_about(self) -> None:
        '''Show about window'''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("This program is needed to create ID3 tags for musical performances and catalog them.")
        msg.setInformativeText("This program is a fork by https://github.com/tcoopman/musictagger")
        msg.setWindowTitle("About")
        msg.exec_()

    def __show_help(self) -> None:
        '''Show help windows'''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            "1.When choosing a scheme, directories and files with the specified tags are created according to the specified scheme with the names of folders and files\n"
            "2.During processing, copies of files with new tags are created and old files change their tags.")
        msg.setInformativeText(
            "Algorithm of actions:\n1. You must select files.\n2. Specify tags without spaces.\n3. Indicate let save.\n4. Press the process button.")
        msg.setWindowTitle("Help")
        msg.exec_()

    def __disable_column(self, index_column: int) -> None:
        '''disable a path column in rows'''
        table = self.tableWidget
        row_count = table.rowCount()
        for i in range(row_count):
            item = table.item(i, index_column)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def __save_file_to(self) -> None:
        '''handler for action save file to'''
        self.__load_path_directory_to_save()
        self.__process()

    def __center(self) -> None:
        '''Set main window at center'''
        frameGm = self.frameGeometry()
        screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(
            PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def __setAligmentTableColumns(self) -> None:
        '''Resize width of column in rows by content'''
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)

    def __exit_from_app(self) -> None:
        '''Exit from app'''
        sys.exit()

    def __load_files_mp3(self) -> None:
        '''Open dialog for choosing mp3 files and load them to table'''
        urls = QFileDialog.getOpenFileUrls(self, 'Open mp3 files', filter='*.mp3')
        return self.__load_urls_to_table(urls[0])

    def __load_file_mp3(self) -> None:
        '''Open dialog for choosing mp3 file and load them to table'''
        urls = QFileDialog.getOpenFileUrl(self, 'Open mp3 file', filter='*.mp3')
        return self.__load_urls_to_table([urls[0]])

    def __load_path_directory_to_save(self) -> None:
        '''Open dialog for choosing path for saving new mp3 files and set path to line'''
        path = QFileDialog.getExistingDirectory(None, "Choose folder for saving music", '.')
        return self.__load_path(path)

    def __load_path(self, path: str) -> None:
        '''Set path BaseDir to TextEdit'''
        self.pathLine.setText(path)

    def __read_file(self, path: str) -> MyMp3:
        ''':return tag mp3file'''
        return MyMp3(path)

    def __load_picture(self, url: str) -> None:
        '''load picture from data mp3 to label or set default image'''
        try:
            tags = ID3(url)
            pict = tags.get("APIC:").data
            im = Image.open(BytesIO(pict))
            qim = ImageQt(im)
            pix = QtGui.QPixmap.fromImage(qim)
            pix.detach()
            self.label_image.setPixmap(pix)
        except Exception:
            self.label_image.setPixmap(QtGui.QPixmap(":/pictures/empty_logo.jpg"))

    def __load_urls_to_table(self, urls: List[QUrl]) -> None:
        '''Load MyMp3 files to table widget'''
        table = self.tableWidget
        for item in urls:
            row = table.rowCount()
            table.setRowCount(row + 1)
            try:
                now_path = item.path()
                mp3 = self.__read_file(now_path)
            except Exception:
                print("Empty path")
                table.setRowCount(row)
            else:
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
        self.__disable_column(6)

    def __select_row(self) -> None:
        '''Selecting row'''
        index = self.tableWidget.selectedIndexes()[-1].row()
        print(index)
        self.__load_picture(self.tableWidget.item(index, self.FILEPATH).text())
        self.__setDescriptionMp3(index)

    def __delete_selected_rows(self) -> None:
        '''Deleting selected rows'''
        count = len([index.row() for index in self.tableWidget.selectedIndexes()])
        for _ in range(count):
            index = self.tableWidget.selectedIndexes()[0].row()
            self.tableWidget.removeRow(index)

    def __setDescriptionMp3(self, indexrow: int) -> None:
        '''Show description of selected mp3 in tables to label'''
        filepath = self.tableWidget.item(indexrow, self.FILEPATH).text()
        file = MP3(filepath)
        filename = file.filename.split('/')[-1]
        desc = f"filename:{filename}\nfilepath:{file.filename}\nlength:{file.info.length} seconds\nchannels:{str(file.info.channels)}\nbitrate:{str(file.info.bitrate)}"
        self.label_description_music.setText(desc)

    def __get_combobox_index(self) -> int:
        '''Get index of current element of combobox'''
        return self.comboBox.currentIndex()

    def __get_row(self, index: int) -> Tuple[str, str, str, str, str, str, str]:
        track = self.tableWidget.item(index, 0).text()
        title = self.tableWidget.item(index, 1).text()
        artist = self.tableWidget.item(index, 2).text()
        album = self.tableWidget.item(index, 3).text()
        disc = self.tableWidget.item(index, 4).text()
        year = self.tableWidget.item(index, 5).text()
        path = self.tableWidget.item(index, 6).text()
        return (track, title, artist, album, disc, year, path)

    def __show_error_message(self, message: str, moreinfo: str) -> None:
        '''Show message box with error'''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setInformativeText(moreinfo)
        msg.setWindowTitle("Error")
        msg.exec_()

    def __check_base_dir_path(self) -> bool:
        '''Check of emty baseDir path'''
        return self.pathLine.text() != ''

    def __check_row(self, row: Tuple[str, str, str, str, str, str, str]) -> bool:
        '''Check row by empty cols'''
        errorMessage = ""
        if row[0] == "": errorMessage += "Track is Empty;"
        if row[1] == "": errorMessage += "Title is Empty;"
        if row[2] == "": errorMessage += "Artist is Empty;"
        if row[3] == "": errorMessage += "Album is Empty;"
        if row[4] == "": errorMessage += "Disc is Empty;"
        if row[5] == "": errorMessage += "Year is Empty;"
        if row[6] == "": errorMessage += "Path is Empty;"
        if errorMessage != "": raise Exception(errorMessage)
        return True

    def __unite_table_records(self, records: List[Tuple[str, str, str, str, str, str, str]], num_field: int) -> List[
        List[Tuple[
            str, str, str, str, str, str, str]]]:
        '''Unit table record by special batches by field'''
        selected_field = set()
        result = []
        len_records = len(records)
        for i in range(len_records):
            sublist = []
            if records[i][num_field] not in selected_field:
                for j in range(i, len_records):
                    if records[i][num_field] == records[j][num_field]:
                        sublist.append(records[j])
                selected_field.add(records[i][num_field])
                result.append(sublist)
        return result

    def __process(self) -> None:
        '''Checking incorrected actions and processing'''
        table = self.tableWidget
        row_count = table.rowCount()
        if row_count == 0:
            self.__show_error_message("Don't selected mp3 files", "Please, add mp3 files")
        else:
            check_errors = True
            rows: List[Tuple[str, str, str, str, str, str, str]] = []
            for row_index in range(row_count):
                row = self.__get_row(row_index)
                try:
                    self.__check_row(row)
                except Exception as e:
                    check_errors = False
                    self.__show_error_message(str(e), 'Please fill in all the gaps')
                    table.selectRow(row_index)
                if check_errors:
                    rows.append(row)
                else:
                    break
            if check_errors:
                if not self.__check_base_dir_path():
                    self.__show_error_message("No save path selected", "Please select a path to save")
                    self.__load_path_directory_to_save()
                else:
                    baseDir = self.pathLine.text()
                    combobox_index = self.__get_combobox_index()
                    schema = self.schems[combobox_index]
                    prepare_rows = self.__unite_table_records(rows, self.schems_numfields[combobox_index])
                    self.progressBar.setValue(0)
                    onepart = 100 / len(prepare_rows)
                    completed = 0
                    sleep(1)
                    for row in prepare_rows:
                        if completed < 100:
                            completed += onepart
                            self.progressBar.setValue(completed)
                        tags = new_build_tags(row, self.builder)
                        mp3s = new_build_fiels(row)
                        process(tags, mp3s, baseDir, schema)
