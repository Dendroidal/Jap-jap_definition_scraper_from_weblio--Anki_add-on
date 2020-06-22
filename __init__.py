# -*- mode: Python; coding: utf-8 -*-
#
# https://github.com/Dendroidal/Jap-jap-definition-scraper-from-weblio--Anki-add-on-
# Author: Luis Alexandre Pereira
#
# Description: Add-on to automatically fetch and format the definitions
# of Japanese words from the online dictionary at weblio.jp
#
# Modules
# definition_formatter - handles the processing of the fetched definitions
# definition_inserter - adds the hooks to anki to fetch the definitions
# notetypes - tests if a note has the requires type
#
# definition_inserter and notetypes are based on the following add-ons
# https://ankiweb.net/shared/info/3918629684
# https://ankiweb.net/shared/info/2055037404

from . import definition_inserter, definition_formatter, notetypes
