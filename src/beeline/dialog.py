from textwrap import dedent

from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import (QCompleter, QDialog, QGroupBox, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout)

from . import beeline
from .anki_util import get_notes
from .config import get as cfg


def show_dialog():
    mw.beeline_dialog = Dialog(mw.app.activeWindow())
    mw.beeline_dialog.show()


class Dialog(QDialog):

    window_title = 'Beeline'

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.resize(500, 100)
        self.setWindowTitle(self.window_title)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # add "tag prefix lineedit"
        self.tag_prefix_lineedit = self._setup_deck_lineedit(layout)

        # add buttons
        layout.beeline_btn = make_button(
            "Beeline", self._on_beeline_button_click, layout)
        layout.beeline_btn = make_button(
            "Unbeeline", self._on_unbeeline_button_click, layout)

    def _setup_deck_lineedit(self, parent):
        groupbox = QGroupBox()
        parent.addWidget(groupbox)
        groupbox.setLayout(QVBoxLayout())

        groupbox.layout().addWidget(QLabel('Choose a deck'))

        self.lineedit = QLineEdit()
        groupbox.layout().addWidget(self.lineedit)
        self.lineedit.setClearButtonEnabled(True)
        self.completer = Completer(self.lineedit, mw.col.decks.allNames())
        self.lineedit.setCompleter(self.completer)

        groupbox.layout().addWidget(QLabel(dedent('''\
            All notes in the selected deck will be changed
            except for the note that is is currently visible.
            In this case just click another note and rerun.
        ''')))

        return self.lineedit

    def _on_beeline_button_click(self):
        if self._warn_if_invalid_deckname():
            return

        notes = get_notes(f'"deck:{self.lineedit.text()}"')
        for note in notes:
            for field in cfg('fields_by_model').get(note.model()['name'], []):
                if 'class="beeline"' in note[field]:
                    continue
                note[field] = beeline.beeline(note[field])

            note.flush()

    def _on_unbeeline_button_click(self):
        if self._warn_if_invalid_deckname():
            return

        notes = get_notes(f'"deck:{self.lineedit.text()}"')
        for note in notes:
            for field in cfg('fields_by_model').get(note.model()['name'], []):
                note[field] = beeline.unbeeline(note[field])

            note.flush()

    def _warn_if_invalid_deckname(self):
        if self.lineedit.text() not in mw.col.decks.allNames():
            showInfo('Please choose a valid deckname')
            return True
        return False


def make_button(txt, f, parent):
    b = QPushButton(txt)
    b.clicked.connect(f)
    parent.addWidget(b)
    return b


class Completer(QCompleter):

    def __init__(self, lineedit, options):
        super().__init__(options)

        self.lineedit = lineedit

        self.setFilterMode(Qt.MatchContains)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        self.model().setStringList(options)

    # show options when lineedit is clicked even if it is empty
    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.setCompletionPrefix(self.lineedit.text())
            self.complete()

        return super().eventFilter(source, event)
