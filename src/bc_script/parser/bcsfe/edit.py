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
        normal_tickets: int | None = None
        rare_tickets: int | None = None
        platinum_tickets: int | None = None
        legend_tickets: int | None = None
        platinum_shards: int | None = None
        np: int | None = None
        leadership: int | None = None
        battle_items: list[int] | dict[str, int] | None = None
        catamins: list[int] | dict[str, int] | None = None
        catseyes: list[int] | dict[str, int] | None = None
        catfruit: list[int] | dict[str, int] | None = None

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

            if self.normal_tickets is not None:
                s.set_normal_tickets(self.normal_tickets)
                bc_script.logger.add_info(
                    f"Set normal tickets to: {self.normal_tickets}"
                )

            if self.rare_tickets is not None:
                prev = s.rare_tickets
                s.set_rare_tickets(self.rare_tickets)
                new = s.rare_tickets
                bc_script.logger.add_info(f"Set rare tickets to: {self.rare_tickets}")

                edit.add_managed_item(s, new - prev, ManagedItemType.RARE_TICKET)

            if self.platinum_tickets is not None:
                prev = s.platinum_tickets
                s.set_platinum_tickets(self.platinum_tickets)
                new = s.platinum_tickets
                bc_script.logger.add_info(
                    f"Set platinum tickets to: {self.platinum_tickets}"
                )

                edit.add_managed_item(s, new - prev, ManagedItemType.PLATINUM_TICKET)

            if self.legend_tickets is not None:
                prev = s.legend_tickets
                s.set_legend_tickets(self.legend_tickets)
                new = s.legend_tickets
                bc_script.logger.add_info(
                    f"Set legend tickets to: {self.legend_tickets}"
                )

                edit.add_managed_item(s, new - prev, ManagedItemType.LEGEND_TICKET)

            if self.platinum_shards is not None:
                s.set_platinum_shards(self.platinum_shards)
                bc_script.logger.add_info(
                    f"Set platinum shards to: {self.platinum_shards}"
                )

            if self.np is not None:
                s.set_np(self.np)
                bc_script.logger.add_info(f"Set np to: {self.np}")

            if self.leadership is not None:
                s.set_leadership(self.leadership)
                bc_script.logger.add_info(f"Set leadership to: {self.leadership}")

            if self.battle_items is not None:

                data = [item.amount for item in s.battle_items.items]

                self.set_grouped_data(self.battle_items, data, "battle_items")
                for i, amount in enumerate(data):
                    s.battle_items.items[i].amount = amount

            if self.catamins is not None:
                self.set_grouped_data(self.catamins, s.catamins, "catamins")

            if self.catseyes is not None:
                self.set_grouped_data(self.catseyes, s.catseyes, "catseyes")

            if self.catfruit is not None:
                self.set_grouped_data(self.catfruit, s.catfruit, "catfruit")

        def set_grouped_data(
            self,
            data: dict[str, int] | list[int] | None,
            save_data: list[int],
            group_name: str,
        ):
            if isinstance(data, list):
                for i, amount in enumerate(data):
                    if i < 0 or i >= len(save_data):
                        bc_script.logger.add_warning(f"Invalid {group_name} index: {i}")
                    else:
                        save_data[i] = amount
            elif isinstance(data, dict):  # type: ignore
                for i, amount in data.items():
                    if i.isdigit():
                        if int(i) < 0 or int(i) >= len(save_data):
                            bc_script.logger.add_warning(
                                f"Invalid {group_name} index: {i}"
                            )
                        else:
                            save_data[int(i)] = amount
                    else:
                        bc_script.logger.add_warning(
                            f"Invalid key for {group_name}: {i}"
                        )
            else:
                bc_script.logger.add_warning(
                    f"Invalid type for {group_name}: {type(data)}"
                )

            bc_script.logger.add_info(f"Set {group_name} to: {data}")
            return save_data
