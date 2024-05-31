from __future__ import annotations

import dataclasses

from bcsfe.core import BackupMetaData, ManagedItem, ManagedItemType, SaveFile

import bc_script
from bc_script.parser.parse import BaseParser


@dataclasses.dataclass
class Edit(BaseParser):
    warn_on_not_found = True
    dict_key: str = "edit"
    basic_items: BasicItems | None = None

    managed_items: list[str] | None = dataclasses.field(
        default_factory=lambda: [s.value for s in ManagedItemType]
    )

    def apply(self, s: SaveFile):
        bc_script.logger.add_info("Applying edit")
        if self.basic_items is not None:
            self.basic_items.apply(s)

    def add_managed_item(self, s: SaveFile, change: int, type: ManagedItemType):
        if self.managed_items is None:
            return
        if type.value in self.managed_items:
            item = ManagedItem.from_change(change, type)
            bc_script.logger.add_info(f"Adding managed item: {item}")
            BackupMetaData(s).add_managed_item(item)

    @dataclasses.dataclass
    class BasicItems(BaseParser):
        dict_key: str = "basic_items"

        catfood: int | None = None
        xp: int | None = None

        def apply(self, s: SaveFile):
            edit = bc_script.ctx.edit
            if edit is None:
                return

            if self.catfood is not None:
                prev = s.catfood
                s.set_catfood(self.catfood)
                new = s.catfood
                bc_script.logger.add_info(f"Set catfood to: {self.catfood}")

                edit.add_managed_item(s, new - prev, ManagedItemType.CATFOOD)

            if self.xp is not None:
                s.set_xp(self.xp)
                bc_script.logger.add_info(f"Set xp to: {self.xp}")
