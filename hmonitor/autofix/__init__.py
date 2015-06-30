# -*- coding: utf-8 -*-

import imp
import logging
import os
import sys

from hmonitor.utils import get_current_file_path
from hmonitor.autofix.scripts import AutoFixBase


autofix_scripts = dict()


def get_autofix_scripts():
    return autofix_scripts


def load_autofix_scripts():
    current_file_path = get_current_file_path(__file__)
    scripts_path = os.path.join(current_file_path, "scripts")
    logging.debug("LOAD AUTOFIX SCRIPTS FROM: {sp}".format(sp=scripts_path))
    files = os.listdir(scripts_path)

    for file_ in files:
        file_ = os.path.join(scripts_path, file_)
        if os.path.isdir(file_):
            continue
        if not file_.endswith(".py") or "__init__.py" in file_:
            continue

        module_name = os.path.split(file_[:-3])[-1]
        if module_name in autofix_scripts:
            logging.warn("{m} ALREADY LOADED, IGNORE IT.".format(
                m=module_name
            ))
        logging.debug("LOAD {m} FROM {f}".format(m=module_name, f=file_))

        sys_mod = None
        if module_name in sys.modules:
            sys_mod = sys.modules[module_name]

        mod = imp.load_source(module_name, file_)
        attrs = dir(mod)
        for attr in attrs:
            attr_ = getattr(mod, attr)
            try:
                base_class = attr_.__bases__
            except:
                # NOTE(tianhuan) do nothing here, just ignore it
                pass
            else:
                if base_class[0] == AutoFixBase:
                    script = attr_()
                    autofix_scripts[module_name] = dict(
                        author=script.get_author(),
                        description=script.get_description(),
                        version=script.get_version(),
                        create_date=script.get_create_date(),
                        mod=script,
                        fix_method=script.do_fix,
                    )

                    del sys.modules[module_name]
                    if sys_mod:
                        sys.modules[module_name] = sys_mod

                    logging.debug("LOAD MODULE {m} SUCCESSFUL".format(
                        m=module_name
                    ))
                    break
        else:
            logging.warn("IGNORE MODULE {m} BECAUSE "
                         "NO SUITABLE CLASS IN IT.".format(m=module_name))

