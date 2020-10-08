# -*- coding: utf-8 -*-
#
# This module detects if a note has the appropriate type
#
# code lifted from the Japanedse Support add-on
# found at https://ankiweb.net/shared/info/3918629684

from aqt import mw
config = mw.addonManager.getConfig(__name__)


def isJapaneseNoteType(noteName):
    noteName = noteName.lower()
    for allowedString in config["noteTypes"]:
        if allowedString.lower() in noteName:
            return True

    return False


def isChineseNoteType(noteName):
    noteName = noteName.lower()
    if 'chinese' in noteName:
        return True

    return False
