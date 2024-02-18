import GoofScript.src.constants as constants
from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor, QFont
import re


class CustomLexer(QsciLexerCustom):
  def __init__(self, parent=None):
    super(CustomLexer, self).__init__(parent)
    # Define a style for blue words
    self.blue_style = 1
    self.setFont(QFont("Consolas", 10))
    self.setColor(QColor("black"))  # Default text color
    # Blue text color for specific words
    self.setColor(QColor("blue"), self.blue_style)

    # The list of words to color blue
    self.blue_words = constants.ALL_TOKENS

  def description(self, style):
    if style == self.blue_style:
      return "Blue Words"
    return ""

  def styleText(self, start, end):
    # Initialize styling process
    self.startStyling(start)

    # Retrieve the text to be styled from the editor
    editor = self.editor()
    if editor is None:
      return

    # Get the text for the specified range from the document
    text = editor.text()[start:end]
    # The setStyling method applies style from the current position, so keep track of the position
    position = 0

    # Use regex to find words
    word_regex = r'\b\w+\b'
    for match in re.finditer(word_regex, text, re.UNICODE):
      # Calculate the length of any non-word text before the matched word
      space_len = match.start() - position
      # Apply the default style to the non-word text
      self.setStyling(space_len, 0)

      # Style the word itself
      word = match.group()
      style = self.blue_style if ((word.lower() in self.blue_words) or (
        word.upper() in self.blue_words))else 0
      self.setStyling(len(word), style)

      # Update the position
      position = match.end()

    # Style the remaining text after the last word
    remaining = len(text) - position
    self.setStyling(remaining, 0)
