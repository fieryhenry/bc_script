from __future__ import annotations

import dataclasses


from bcsfe.core import BackupMetaData, ManagedItem, ManagedItemType, SaveFile

import bc_script
from bc_script.parser.parse import BaseParser
from bc_script.parser.bcsfe.basic_items import BasicItems
from bc_script.parser.bcsfe.cats import Cats

import bcsfe


@dataclasses.dataclass
class Edit(BaseParser):
    warn_on_not_found = True
    dict_key: str = "edit"

    basic_items: bc_script.parser.bcsfe.basic_items.BasicItems | None = None
    cats: bc_script.parser.bcsfe.cats.Cats | None = None

    managed_items: list[str] | None = dataclasses.field(
        default_factory=lambda: [s.value.lower() for s in ManagedItemType]
    )

    forced_locale: str | None = None

    def apply(self, s: SaveFile):
        bc_script.logger.add_info("Applying edit")
        if self.forced_locale is not None:
            bcsfe.core.core_data.config.config[
                bcsfe.core.ConfigKey.FORCE_LANG_GAME_DATA
            ] = True
            bcsfe.core.core_data.config.config[bcsfe.core.ConfigKey.LOCALE] = (
                self.forced_locale
            )
        if self.basic_items is not None:
            self.basic_items.apply(s)
        if self.cats is not None:
            self.cats.apply(s)

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
    ]
