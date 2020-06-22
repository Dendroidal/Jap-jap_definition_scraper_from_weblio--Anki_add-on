# -*- coding: utf-8 -*-
#
# automatic definition generation from weblio.jp

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

dicSrcFields = config['dicSrcFields']
defFields = config['defFields']


# Variables (can be edited on Addons > Config)
expressionField = config['dicSrcFields'][0]  # config['expressionField']
definitionField = config['defFields'][0]  # config['definitionField']
# keybinding = config['keybinding']

# Labels
# text shown while processing cards
label_progress_update = 'Fetching definitions...'
# text shown on menu to run the functions
label_menu = 'Regenerate definitions'


# Fetches definition for a note
##########################################################################

def note_def_fetch(note, srcfld):
    words = note[srcfld].split("、")

    dic = {}

    for word in words:
        dic[word] = {}
        dic[word]['data'] = WordData(word)
        dic[word]['thread'] = \
            threading.Thread(target=dic[word]['data'].fetch_def)
        dic[word]['thread'].start()

    for word in words:
        dic[word]['thread'].join()

    defns = sum((dic[word]['data'].definitions for word in words), [])
    return "".join(defn.display_def() for defn in defns)


# Focus lost hook
##########################################################################


def onFocusLost(flag, note, fidx):
    src = None
    dst = None
    # japanese model?
    if not isJapaneseNoteType(note.model()['name']):
        return flag
    # have src and dst fields?
    fields = mw.col.models.fieldNames(note.model())
    src = fields[fidx]
    # Retro compatibility
    if src in dicSrcFields:
        srcIdx = dicSrcFields.index(src)
        dst = defFields[srcIdx]
    if not src or not dst:
        return flag
    # dst field exists?
    if dst not in note:
        return flag
    # dst field already filled?
    if note[dst]:
        return flag
    # checks for source text
    if not mw.col.media.strip(note[src]):
        return flag

    note[dst] = note_def_fetch(note, src)

    return True


# Bulk definition fetcher
#################################

class Regen():
    def __init__(self, ed, fids):
        self.ed = ed
        self.fids = fids
        self.completed = 0
        self.config = mw.addonManager.getConfig(__name__)
        # self.force_update = config['force_update']
        # self.update_separator = config['update_separator']
        self.sema = threading.BoundedSemaphore(config['max_threads'])
        self.values = {}
        if len(self.fids) == 1:  # Single card selected
            self.row = self.ed.currentRow()
            self.ed.form.tableView.selectionModel().clear()
        mw.progress.start(max=len(self.fids), immediate=True)
        mw.progress.update(
            label=label_progress_update,
            value=0)

    def prepare(self):
        fs = [mw.col.getNote(id=fid) for fid in self.fids]
        i = 0
        for f in fs:
            try:
                if self.config['force_update'] == 'no' and f[definitionField]:
                    self.completed += 1
                    mw.progress.update(
                        label=label_progress_update,
                        value=self.completed)
                else:
                    self.values[i] = {}
                    self.values[i]['f'] = f
                    self.values[i]['word'] = f[expressionField]
                    thread = threading.Thread(target=self.fetch_def,
                                              args=(i,))
                    self.values[i]['thread'] = thread
                    thread.start()
                    i += 1
            except:
                print('definitions failed:')
                traceback.print_exc()

    def fetch_def(self, i):
        with self.sema:
            self.values[i]['definition'] = note_def_fetch(self.values[i]['f'],
                                                          expressionField)

    def wait_threads(self):
        for i, _ in self.values.items():
            thread = self.values[i]['thread']
            thread.join()
            self.update_def(i)
        mw.progress.finish()
        if len(self.fids) == 1:
            self.ed.form.tableView.selectRow(self.row)

    def update_def(self, i):
        f = self.values[i]['f']
        try:
            if self.config['force_update'] == "append":
                if f[definitionField]:
                    f[definitionField] += self.config['update_separator']
                f[definitionField] += self.values[i]['definition']
            else:
                f[definitionField] = self.values[i]['definition']
        except:
            print('definitions failed:')
            traceback.print_exc()
        try:
            f.flush()
        except:
            raise Exception()
        self.completed += 1
        mw.progress.update(
            label=label_progress_update,
            value=self.completed)


def setupMenu(ed):
    a = QAction(label_menu, ed)
    a.triggered.connect(lambda _, e=ed: onRegenGlosses(e))
    ed.form.menuEdit.addAction(a)
#    a.setShortcut(QKeySequence(keybinding))


def addToContextMenu(view, menu):
    menu.addSeparator()
    a = menu.addAction(label_menu)
    a.triggered.connect(lambda _, e=view: onRegenGlosses(e))
#    a.setShortcut(QKeySequence(keybinding))


def onRegenGlosses(ed):
    regen = Regen(ed, ed.selectedNotes())
    regen.prepare()
    regen.wait_threads()
    mw.requireReset()


# Init
##########################################################################
addHook('editFocusLost', onFocusLost)
addHook('browser.setupMenus', setupMenu)
addHook('browser.onContextMenu', addToContextMenu)
