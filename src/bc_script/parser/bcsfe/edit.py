from __future__ import annotations

import dataclasses
import typing


from bcsfe.core import BackupMetaData, ManagedItem, ManagedItemType, SaveFile

import bc_script
from bc_script.parser.parse import BaseParser
from bc_script.parser.bcsfe.basic_items import BasicItems
from bc_script.parser.bcsfe.cats import Cats
from bc_script.parser.bcsfe.special_skills import SpecialSkills

import bcsfe

from typeguard import typechecked


@dataclasses.dataclass
class Edit(BaseParser):
    warn_on_not_found = True
    dict_key: str = "edit"

    basic_items: bc_script.parser.bcsfe.basic_items.BasicItems | None = None
    cats: bc_script.parser.bcsfe.cats.Cats | None = None
    special_skills: bc_script.parser.bcsfe.special_skills.SpecialSkills | None = None

    managed_items: list[str] | None = dataclasses.field(
        default_factory=lambda: [s.value.lower() for s in ManagedItemType]
    )

    forced_locale: str | None = None

    @typechecked
    def __new__(
        cls,
        managed_items: list[str] | None = None,
        forced_locale: str | None = None,
        **kwargs: typing.Any,
    ):
        return super().__new__(cls)

    def apply(self, s: SaveFile):
        bc_script.logger.add_info("Applying edit")
        if self.forced_locale is not None:
            bcsfe.core.core_data.config.config[
                bcsfe.core.ConfigKey.FORCE_LANG_GAME_DATA
            ] = True
            bcsfe.core.core_data.config.config[bcsfe.core.ConfigKey.LOCALE] = (
                self.forced_locale
            )
            bc_script.logger.add_info(f"Forcing locale: {self.forced_locale}")
        if self.basic_items is not None:
            self.basic_items.apply(s)
        if self.cats is not None:
            self.cats.apply(s)
        if self.special_skills is not None:
            self.special_skills.apply(s)

    def add_managed_item(self, s: SaveFile, change: int, type: ManagedItemType):
        if self.managed_items is None:
            return
        if type.value.lower() in self.managed_items:
            item = ManagedItem.from_change(change, type)
            bc_script.logger.add_info(f"Adding managed item: {item}")
            BackupMetaData(s).add_managed_item(item)

    subclasses = [
        BasicItems,
        Cats,
        SpecialSkills,
    ]
