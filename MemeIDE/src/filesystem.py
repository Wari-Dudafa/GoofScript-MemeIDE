from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QModelIndex, Qt
import sys


class FileSystemModel(QFileSystemModel):
  def __init__(self, parent=None):
    super().__init__(parent)
    # Load your custom icon here. Make sure to adjust the path to where your icon is stored.
    self.customIcon = QIcon('./MemeIDE/assets/logo/GoofyIcon.ico')

  def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
    if role == Qt.DecorationRole:
      # Check if the file has a .goof extension
      if index.isValid() and self.fileInfo(index).suffix().lower() == 'goof':
        return self.customIcon
    return super().data(index, role)
