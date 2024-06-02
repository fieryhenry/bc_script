from __future__ import annotations

import dataclasses
import typing

from typeguard import typechecked

from bc_script.parser.parse import BaseParser


@dataclasses.dataclass
class Info(BaseParser):
    warn_on_not_found = True
    dict_key: str = "info"

    name: str = ""
    description: str = ""
    author: str = ""
    version: str = "1.0.0"

    @typechecked
    def __new__(
        cls,
        name: str = "",
        description: str = "",
        author: str = "",
        version: str = "1.0.0",
        **kwargs: typing.Any,
    ):
        return super().__new__(cls)
