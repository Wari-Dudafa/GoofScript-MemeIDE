import sys
import MemeIDE.src.main as memeide_main
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *


stylesheet = """
    QTreeView, QsciScintilla {
        border: 3px solid black; 
        color: black; 
        background-color: white;
    }
"""

if __name__ == '__main__':
  app = QApplication([])
  app.setStyleSheet(stylesheet)
  window = memeide_main.MainWindow()
  sys.exit(app.exec())
