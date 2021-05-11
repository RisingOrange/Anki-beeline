from anki.hooks import addHook
from .dialog import show_dialog


def setup_menu(self):
    a = self.menuBar().addAction('Beeline')
    a.triggered.connect(lambda _: show_dialog())


addHook('browser.setupMenus', lambda self: setup_menu(self))
