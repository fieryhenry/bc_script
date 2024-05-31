from __future__ import annotations

import dataclasses


from bcsfe.core import BackupMetaData, ManagedItem, ManagedItemType, SaveFile
import bcsfe

import bc_script
from bc_script.parser.parse import BaseParser


@dataclasses.dataclass
class Edit(BaseParser):
    warn_on_not_found = True
    dict_key: str = "edit"
    basic_items: BasicItems | None = None
    cats: Cats | None = None

    managed_items: list[str] | None = dataclasses.field(
        default_factory=lambda: [s.value for s in ManagedItemType]
    )

    def apply(self, s: SaveFile):
        bc_script.logger.add_info("Applying edit")
        if self.basic_items is not None:
            self.basic_items.apply(s)
        if self.cats is not None:
            self.cats.apply(s)

    def add_managed_item(self, s: SaveFile, change: int, type: ManagedItemType):
        if self.managed_items is None:
            return
        if type.value in self.managed_items:
            item = ManagedItem.from_change(change, type)
            bc_script.logger.add_info(f"Adding managed item: {item}")
            BackupMetaData(s).add_managed_item(item)

    @dataclasses.dataclass
    class Cats(BaseParser):
        dict_key: str = "cats"

        cats: list[CatEdit] | None = None

        def apply(self, s: SaveFile):
            edit = bc_script.ctx.edit
            if edit is None:
                return

            if self.cats is not None:
                for cat in self.cats:
                    cat.apply(s)

            s.max_rank_up_sale()

        @dataclasses.dataclass
        class CatEdit(BaseParser):
            dict_key: str = "cat"

            ids: list[int] | None | str | list[str] = None

            unlock: bool | None = None

            upgrade: list[int | str] | None = None
            upgrade_base: int | str | None = None
            upgrade_plus: int | str | None = None

            true_form: bool | None = None
            ultra_form: bool | None = None
            set_current_forms: bool = False
            force_forms: bool = False

            def apply(self, s: SaveFile):
                edit = bc_script.ctx.edit
                if edit is None:
                    return

                if self.ids is not None:
                    if self.ids == "all":
                        cats = s.cats.get_all_cats()
                    elif self.ids == "unlocked":
                        cats = s.cats.get_unlocked_cats()
                    elif self.ids == "non_unlocked":
                        cats = s.cats.get_non_unlocked_cats()
                    elif self.ids == "obtainable":
                        cats = s.cats.get_cats_obtainable(s) or []
                    else:
                        if not isinstance(self.ids, list):
                            ids = [self.ids]
                        else:
                            ids = self.ids

                        cats: list[bcsfe.core.Cat] = []

                        for id in ids:
                            id = str(id)
                            if id.isdigit():
                                cat = s.cats.get_cat_by_id(int(id))
                                if cat is not None:
                                    cats.append(cat)
                            elif id.startswith("rarity-"):
                                rarity = int(id.split("-")[1])
                                cats.extend(s.cats.get_cats_rarity(s, rarity))
                            elif id.startswith("banner-"):
                                banner = int(id.split("-")[1])
                                cats.extend(
                                    s.cats.get_cats_gatya_banner(s, banner) or []
                                )
                            else:
                                bc_script.logger.add_warning(f"Invalid cat id: {id}")

                    self.set_cats(s, cats)

            def set_cats(self, s: SaveFile, cats: list[bcsfe.core.Cat]):
                if self.true_form is not None:
                    if self.true_form:
                        s.cats.true_form_cats(
                            s, cats, self.force_forms, self.set_current_forms
                        )
                        bc_script.logger.add_info("Set true form for cats")
                    else:
                        for cat in cats:
                            cat.remove_true_form()
                            bc_script.logger.add_info(
                                f"Removed true form for cat: {cat.id}"
                            )

                if self.ultra_form is not None:
                    if self.ultra_form:
                        s.cats.fourth_form_cats(
                            s, cats, self.force_forms, self.set_current_forms
                        )
                        bc_script.logger.add_info("Set ultra form for cats")
                    else:
                        for cat in cats:
                            cat.remove_fourth_form()
                            bc_script.logger.add_info(
                                f"Removed ultra form for cat: {cat.id}"
                            )

                for cat in cats:
                    if self.unlock is not None:
                        cat.unlock(s) if self.unlock else cat.reset()
                        bc_script.logger.add_info(
                            f"{'Unlocked' if self.unlock else 'Removed'} cat: {cat.id}"
                        )

                    self.upgrade_cat(cat, s)

            def upgrade_cat(self, cat: bcsfe.core.Cat, s: SaveFile):
                if self.upgrade is not None:
                    if len(self.upgrade) != 2:
                        bc_script.logger.add_warning(
                            f"Invalid upgrade data: {self.upgrade}"
                        )

                    upgrade_base = self.get_base(cat, s)
                    upgrade_plus = self.get_plus(cat, s)

                    if upgrade_base is None or upgrade_plus is None:
                        return

                    upgrade = bcsfe.core.Upgrade(
                        plus=upgrade_plus, base=upgrade_base - 1
                    )
                    cat.set_upgrade(s, upgrade)
                    bc_script.logger.add_info(
                        f"Set upgrade for cat: {cat.id} to {upgrade.base+1}+{upgrade.plus}"
                    )

                if self.upgrade_base is not None:
                    upgrade_base = self.get_base(cat, s)
                    if upgrade_base is None:
                        return
                    upgrade = cat.upgrade
                    upgrade.base = upgrade_base - 1
                    cat.set_upgrade(s, upgrade)
                    bc_script.logger.add_info(
                        f"Set upgrade base for cat: {cat.id} to {upgrade.base+1}"
                    )

                if self.upgrade_plus is not None:
                    upgrade_plus = self.get_plus(cat, s)
                    if upgrade_plus is None:
                        return
                    upgrade = cat.upgrade
                    upgrade.plus = upgrade_plus
                    cat.set_upgrade(s, upgrade)
                    bc_script.logger.add_info(
                        f"Set upgrade plus for cat: {cat.id} to +{upgrade.plus}"
                    )

            def get_base(self, cat: bcsfe.core.Cat, s: SaveFile):
                powerup = bcsfe.core.PowerUpHelper(cat, s)
                if self.upgrade is None:
                    return None

                if (
                    isinstance(self.upgrade[0], str)
                    and not str(self.upgrade[0]).isdigit()
                ):
                    if self.upgrade[0] == "max":
                        upgrade_base = powerup.get_max_possible_base()
                    else:
                        bc_script.logger.add_warning(
                            f"Invalid upgrade base: {self.upgrade[0]}"
                        )
                        return None
                else:
                    upgrade_base = int(self.upgrade[0])

                return upgrade_base

            def get_plus(self, cat: bcsfe.core.Cat, s: SaveFile):
                powerup = bcsfe.core.PowerUpHelper(cat, s)
                if self.upgrade is None:
                    return None

                if (
                    isinstance(self.upgrade[1], str)
                    and not str(self.upgrade[1]).isdigit()
                ):
                    if self.upgrade[1] == "max":
                        upgrade_plus = powerup.get_max_possible_plus()
                    else:
                        bc_script.logger.add_warning(
                            f"Invalid upgrade plus: {self.upgrade[1]}"
                        )
                        return None
                else:
                    upgrade_plus = int(self.upgrade[1])

                return upgrade_plus

        list_cls = CatEdit

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
