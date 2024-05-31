from __future__ import annotations

import dataclasses

from bc_script.parser.parse import BaseParser


@dataclasses.dataclass
class Pkg(BaseParser):
    error_on_not_found: bool = True
    dict_key: str = "pkg"

    schema: str = "bcsfe"
    version: str = "3.0.0"
