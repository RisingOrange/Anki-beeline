from aqt import mw


def get_notes(search_string):
    return [
        mw.col.getNote(id)
        for id in mw.col.find_notes(search_string)
    ]
