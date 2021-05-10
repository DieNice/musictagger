import sys
from src.main_app import MainApp
from PyQt5 import QtWidgets
from src.rename import TagDictBuilderLine
from src.process import build_tags, build_files, process

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()