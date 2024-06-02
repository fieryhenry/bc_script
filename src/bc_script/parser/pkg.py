from __future__ import annotations

import dataclasses
import typing

from bc_script.parser.parse import BaseParser
from typeguard import typechecked


@dataclasses.dataclass
class Pkg(BaseParser):
    error_on_not_found: bool = True
    dict_key: str = "pkg"

    schema: str = "bcsfe"
    version: str = "3.0.0"

    @typechecked
    def __new__(
        cls, schema: str = "bcsfe", version: str = "3.0.0", **kwargs: typing.Any
    ):
        return super().__new__(cls)
