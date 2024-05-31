from __future__ import annotations

import dataclasses

from bc_script.parser.parse import BaseParser


@dataclasses.dataclass
class Info(BaseParser):
    warn_on_not_found = True
    dict_key: str = "info"

    name: str = ""
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
