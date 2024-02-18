from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
import webbrowser
from io import StringIO
import MemeIDE.src.lexer as lexer
import MemeIDE.src.filesystem as filesystem
import GoofScript.src.main as goof_main
from pathlib import Path
import sys


class MainWindow(QMainWindow):
  def __init__(self):
    super(QMainWindow, self).__init__()
    self.body_clr = "#ADD8E6"
    self.init_ui()
    self.current_file_path = None
    self.current_folder_path = None
    self.current_file = None

  def init_ui(self):
    self.setWindowTitle("MemeIDE")
    self.resize(1300, 900)
    self.setWindowIcon(QIcon('./MemeIDE/assets/logo/GoofyIcon.ico'))

    self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.body_clr};
            }}
            """ + open("./MemeIDE/src/css/style.qss", "r").read())

    # font needs to be installed on computer
    self.window_font = QFont("Microsoft Sans Serif")
    self.window_font.setPointSize(12)
    self.setFont(self.window_font)
    self.set_up_menu()
    self.set_up_body()
    self.open_folder(QDir.homePath())
    self.show()

  def run_file(self):

    # Backup the original stdout
    original_stdout = sys.stdout

    # Create a string buffer to capture the prints
    sys.stdout = StringIO()

    if self.current_file_path:
      if ".goof" in self.current_file_path:

        goof_main.main(self.current_file_path)

        # Get the value from the buffer
        captured_output = sys.stdout.getvalue()

        # Restore the original stdout
        sys.stdout = original_stdout

        # Create a new window to display the output

        QMessageBox.information(self, "Output", captured_output)
      else:
        QMessageBox.warning(
          self, "No GoofScript", "There is no GoofScript file currently open to run.")
    else:
      QMessageBox.warning(
        self, "No file", "There is no file currently open to run.")

  def set_up_menu(self):
    menu_bar = self.menuBar()

    # File Menu
    file_menu = menu_bar.addMenu("File")

    save_file = file_menu.addAction("Save")
    save_file.setShortcut("Ctrl+S")
    save_file.triggered.connect(self.save_file)

    open_file = file_menu.addAction("Open File")
    open_file.setShortcut("Ctrl+O")
    open_file.triggered.connect(self.open_file)

    open_folder = QAction('Open Folder', self)
    open_folder.setShortcut('Ctrl+Shift+O')
    open_folder.triggered.connect(self.open_folder)
    file_menu.addAction(open_folder)

    close_file = file_menu.addAction("Close File")
    close_file.setShortcut("Ctrl+C")
    close_file.triggered.connect(self.close_file)

    new_file = file_menu.addAction("New File")
    new_file.setShortcut("Ctrl+N")
    new_file.triggered.connect(self.new_file)

    # death menu
    edit_menu = menu_bar.addMenu("Dont Click Me")

    dont_click_me = edit_menu.addAction("I said dont click me")
    dont_click_me.triggered.connect(self.open_death)

    # run code
    run_menu = menu_bar.addMenu("Run")
    run_action = run_menu.addAction("Run File")
    run_action.setShortcut("Ctrl+R")
    run_action.triggered.connect(self.run_file)

  def open_folder(self, path=None):
    if not path:
      dir_path = QFileDialog.getExistingDirectory(
        self, 'Open Folder', QDir.homePath())
    else:
      dir_path = path  # Use the provided path argument
    if dir_path:
      self.directory_view.setRootIndex(
        self.file_system_model.setRootPath(dir_path))

    self.current_folder_path = dir_path

  def close_file(self):
    # Check if there are unsaved changes
    if self.text_edit.document().isModified():
      reply = QMessageBox.question(self, 'Close File', "You have unsaved changes. Do you want to save them before closing?",
                                   QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

      if reply == QMessageBox.Save:
        self.save_file()  # Save the file
      elif reply == QMessageBox.Cancel:
        return  # Do not close the file if the user cancels

    # Proceed to close the file
    self.text_edit.clear()
    self.current_file_path = None
    self.file_name_label.setText("No file opened")
    self.statusBar().showMessage("File closed", 2000)

  def save_file(self):
    if self.current_file_path:
      # Save the current content to the file
      with open(self.current_file_path, 'w', encoding='utf-8') as file:
        file.write(self.text_edit.text())
      self.statusBar().showMessage(f"Saved {self.current_file_path}", 2000)

  def open_file(self):
    # Open a file dialog to select a .txt file
    file_name, _ = QFileDialog.getOpenFileName(
      self, "Open File", QDir.homePath(), "GoofScript files(*.goof);;Text files (*.txt)")

    # Check if a file was selected
    if file_name:
      self.current_file_path = file_name
      # Read the content of the file
      with open(file_name, 'r', encoding='utf-8') as file:
        file_content = file.read()

      # Display the content in the editor
      self.display_file_content(file_content, file_name)

  def open_death(self):
    webbrowser.open('https://www.youtube.com/watch?v=xvFZjo5PgG0', new=2)

  def display_file_content(self, content):
    self.text_edit.setText(content)

  def display_file_content(self, content, file_name):
    self.text_edit.setText(content)
    # Display just the file name
    self.file_name_label.setText(Path(file_name).name)

  def set_up_body(self):
    # Main horizontal layout
    main_layout = QHBoxLayout()

    # File explorer
    self.file_system_model = filesystem.FileSystemModel()
    self.file_system_model.setRootPath(QDir.homePath())
    self.directory_view = QTreeView()

    self.file_system_model.setReadOnly(False)
    self.directory_view.setModel(self.file_system_model)

    self.directory_view.hideColumn(1)  # hide size
    self.directory_view.hideColumn(2)  # hide type
    self.directory_view.hideColumn(3)  # hide date modified
    self.directory_view.setVisible(True)
    self.directory_view.setHeaderHidden(True)
    self.directory_view.clicked.connect(self.open_file_from_tree)

    # Pink body area
    self.body_frame = QFrame()
    self.body_frame.setFrameShape(QFrame.NoFrame)
    self.body_frame.setFrameShadow(QFrame.Plain)
    self.body_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
    body_layout = QVBoxLayout()

    body_layout = QVBoxLayout()
    body_layout.setSpacing(0)
    body_layout.setContentsMargins(10, 0, 0, 0)

    self.body_frame.setLayout(body_layout)

    # Label for displaying the file name
    self.file_name_label = QLabel("No file opened")
    self.file_name_label.setFont(QFont("Arial", 14))
    self.file_name_label.setAlignment(Qt.AlignCenter)
    # Set the background color of the label to grey
    # and add some padding for aesthetic purposes
    self.file_name_label.setStyleSheet("""
            background-color: white;
            padding: 5px;
            border-radius: 5px;
            border: 3px solid black;
        """)
    self.file_name_label.setSizePolicy(
      QSizePolicy.Preferred, QSizePolicy.Maximum)

    body_layout.addWidget(self.file_name_label)

    spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
    body_layout.addItem(spacer)

    # QsciScintilla editor
    self.text_edit = QsciScintilla()
    self.text_edit.setFont(QFont("Consolas", 10))

    # Set my lexer
    self.custom_lexer = lexer.CustomLexer(self.text_edit)
    self.text_edit.setLexer(self.custom_lexer)

    # Enable line numbers with the margin
    self.text_edit.setMarginsFont(self.text_edit.font())
    self.text_edit.setMarginWidth(0, QFontMetrics(
      self.text_edit.font()).width("0000") + 6)
    self.text_edit.setMarginLineNumbers(0, True)

    # added to the body_frame widget children
    body_layout.addWidget(self.text_edit)

    # Splitter to allow resizing
    self.hsplit = QSplitter(Qt.Horizontal)
    self.hsplit.addWidget(self.directory_view)
    self.hsplit.addWidget(self.body_frame)

    # Set the initial sizes of the splitter to make the directory view and text editor share the space equally
    total_width = self.width()
    self.hsplit.setSizes([total_width // 4, 3 * total_width // 4])

    main_layout.addWidget(self.hsplit)

    # Set the main layout to the central widget
    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    self.setCentralWidget(central_widget)
    self.directory_view.setModel(self.file_system_model)

  def open_file_from_tree(self, file_index):
    file_path = self.file_system_model.filePath(file_index)

    # Check if the selected item is a file
    if QFileInfo(file_path).isFile():
      self.current_file_path = file_path
      # Read the content of the file
      with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        # Display just the file name
        self.file_name_label.setText(
          QFileInfo(file_path).fileName().replace(".goof", ""))
      # Display the content in the editor
      self.text_edit.setText(file_content)

  def new_file(self):
    reply = QMessageBox.question(self, 'New File', "You may have unsaved changes. Do you want to save them before creating a new .goof file?",
                                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

    if reply == QMessageBox.Save:
      self.save_file()  # Save the current file
      # After saving, proceed to create a new file
      self.create_and_open_new_goof_file()
    elif reply == QMessageBox.Discard:
      # Directly create a new file without saving
      self.create_and_open_new_goof_file()
    elif reply == QMessageBox.Cancel:
      return  # Do not create a new file if the user cancels

  def create_and_open_new_goof_file(self):
    if not self.current_folder_path:
      # If the current folder path is not set, open the folder dialog
      self.open_folder()
      return

    # Define the new file path for the .goof file in the current directory
    file_name = "new_file.goof"
    new_file_path = self.current_folder_path + "/" + file_name
    # Open (or create if doesn't exist) the file for writing and close it to make sure it exists
    with open(new_file_path, 'w') as file:
      file.write("")  # Writing an empty string to ensure the file is created
    # Set the current file path to the new file
    self.current_file_path = new_file_path
    # Update the editor and file name label to reflect the new file
    self.text_edit.clear()
    self.file_name_label.setText(file_name)
    self.statusBar().showMessage(
      f"New .goof file created: {file_name}", 2000)
