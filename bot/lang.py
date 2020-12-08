import gettext

import db
import utils


def locale_path():
    return utils.current_path() + "/locale"


def install(caller, update=None, lang=None):
    if lang is None:
        lang = db.lang_check(caller, update)
    default_lang = gettext.translation(
        caller, localedir=locale_path(), languages=[lang])
    default_lang.install()
