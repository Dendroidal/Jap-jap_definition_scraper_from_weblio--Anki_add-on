# -*- coding: utf-8 -*-
#
# this module adds the hooks that allow anki to fetch definitions
# when creating/editing a single card
# and bulk fetch then browsing multiple cards
#
# creating/editing code is based on the Japanedse Support add-on
# found at https://ankiweb.net/shared/info/3918629684
# bulk fetch code is based on the weblio scrapper add-on by renato
# found at https://ankiweb.net/shared/info/2055037404

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from anki.hooks import addHook

import threading
import traceback

#####

from .notetypes import isJapaneseNoteType
from .definition_formatter import WordData

from aqt import mw
config = mw.addonManager.getConfig(__name__)

# Variables (can be edited on Addons -> Config)
dicSrcFields = config['dicSrcFields']
defFields = config['defFields']

expressionField = config['dicSrcFields'][0]  # config['expressionField']
definitionField = config['defFields'][0]  # config['definitionField']
# keybinding = config['keybinding']

# Labels
# text shown while processing cards
label_progress_update = 'Fetching definitions...'
# text shown on menu to run the functions
label_menu = 'Regenerate definitions'


# Fetches definition for a single note
##########################################################################

def note_def_fetch(note, srcfld):
    words = note[srcfld].split("、")

    word_info = {}

    for word in words:
        word_info[word] = {}
        word_info[word]['data'] = WordData(word)
        word_info[word]['thread'] = \
            threading.Thread(target=word_info[word]['data'].fetch_def)
        word_info[word]['thread'].start()

    for word in words:
        word_info[word]['thread'].join()

    defns = sum((word_info[word]['data'].definitions for word in words), [])
    return "".join(defn.display_def() for defn in defns)


# Focus lost hook
##########################################################################


def onFocusLost(flag, note, field_idx):
    src = None
    dst = None
    # is the note a japanese model?
    if not isJapaneseNoteType(note.model()['name']):
        return flag
    # does the note have src and dst fields?
    fields = mw.col.models.fieldNames(note.model())
    src = fields[field_idx]
    # Retro compatibility
    if src in dicSrcFields:
        srcIdx = dicSrcFields.index(src)
        dst = defFields[srcIdx]
    if not src or not dst:
        return flag
    # does dst field exist?
    if dst not in note:
        return flag
    # is dst field already filled?
    if note[dst]:
        return flag
    # checks if there is source text
    if not mw.col.media.strip(note[src]):
        return flag

    # fetches definition data and fills the dst field
    note[dst] = note_def_fetch(note, src)

    return True


# Bulk definition fetcher
#################################

class BulkGenerator():
    def __init__(self, browser, note_ids):
        self.browser = browser
        self.note_ids = note_ids
        self.completed = 0
        self.config = mw.addonManager.getConfig(__name__)
        self.semaphore = threading.BoundedSemaphore(config['max_threads'])
        self.values = {}
        if len(self.note_ids) == 1:  # Single card selected
            self.row = self.browser.currentRow()
            self.browser.form.tableView.selectionModel().clear()
        mw.progress.start(max=len(self.note_ids), immediate=True)
        mw.progress.update(
            label=label_progress_update,
            value=0)

    def prepare(self):
        notes = [mw.col.getNote(id=note_id) for note_id in self.note_ids]
        i = 0
        for note in notes:
            try:
                if self.config['force_update'] == 'no' and note[definitionField]:
                    self.completed += 1
                    mw.progress.update(
                        label=label_progress_update,
                        value=self.completed)
                else:
                    self.values[i] = {}
                    self.values[i]['note'] = note
                    self.values[i]['word'] = note[expressionField]
                    thread = threading.Thread(target=self.fetch_def,
                                              args=(i,))
                    self.values[i]['thread'] = thread
                    thread.start()
                    i += 1
            except:
                print('definitions failed:')
                traceback.print_exc()

    def fetch_def(self, i):
        with self.semaphore:
            self.values[i]['definition'] = note_def_fetch(self.values[i]['note'],
                                                          expressionField)

    def wait_threads(self):
        for i in self.values.keys():
            thread = self.values[i]['thread']
            thread.join()
            self.update_def(i)
        mw.progress.finish()
        if len(self.note_ids) == 1:
            self.browser.form.tableView.selectRow(self.row)

    def update_def(self, i):
        note = self.values[i]['note']
        try:
            if self.config['force_update'] == "append":
                if note[definitionField]:
                    note[definitionField] += self.config['update_separator']
                note[definitionField] += self.values[i]['definition']
            else:
                note[definitionField] = self.values[i]['definition']
        except:
            print('definitions failed:')
            traceback.print_exc()
        try:
            note.flush()
        except:
            raise Exception()
        self.completed += 1
        mw.progress.update(
            label=label_progress_update,
            value=self.completed)


def setupMenu(browser):
    a = QAction(label_menu, browser)
    a.triggered.connect(lambda: bulkFetcher(browser))
    browser.form.menuEdit.addAction(a)
#    a.setShortcut(QKeySequence(keybinding))


def onContextMenu(browser, menu):
    menu.addSeparator()
    a = menu.addAction(label_menu)
    a.triggered.connect(lambda: bulkFetcher(browser))
#    a.setShortcut(QKeySequence(keybinding))


def bulkFetcher(browser):
    bulkgenerator = BulkGenerator(browser, browser.selectedNotes())
    bulkgenerator.prepare()
    bulkgenerator.wait_threads()
    mw.requireReset()


# Init
#############################################################

addHook('editFocusLost', onFocusLost)
addHook('browser.setupMenus', setupMenu)
addHook('browser.onContextMenu', onContextMenu)
