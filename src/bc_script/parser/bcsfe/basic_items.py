from __future__ import annotations

import dataclasses


from bcsfe.core import ManagedItemType, SaveFile, OrbInfoList

import bc_script
from bc_script.parser.parse import BaseParser


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

    talent_orbs: TalentOrbs | None = None

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
            bc_script.logger.add_info(f"Set normal tickets to: {self.normal_tickets}")

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
            bc_script.logger.add_info(f"Set legend tickets to: {self.legend_tickets}")

            edit.add_managed_item(s, new - prev, ManagedItemType.LEGEND_TICKET)

        if self.platinum_shards is not None:
            s.set_platinum_shards(self.platinum_shards)
            bc_script.logger.add_info(f"Set platinum shards to: {self.platinum_shards}")

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

        if self.talent_orbs is not None:
            self.talent_orbs.apply(s)

    def set_grouped_data(
        self,
        data: dict[str, int] | list[int] | None,
        save_data: list[int],
        group_name: str,
    ):
        if isinstance(data, list):
            for i, amount in enumerate(data):
                if i < 0 or i >= len(save_data):
                    bc_script.logger.add_error(f"Invalid {group_name} index: {i}")
                else:
                    save_data[i] = amount
        elif isinstance(data, dict):  # type: ignore
            for i, amount in data.items():
                if i.isdigit():
                    if int(i) < 0 or int(i) >= len(save_data):
                        bc_script.logger.add_error(f"Invalid {group_name} index: {i}")
                    else:
                        save_data[int(i)] = amount
                else:
                    bc_script.logger.add_error(f"Invalid key for {group_name}: {i}")
        else:
            bc_script.logger.add_error(f"Invalid type for {group_name}: {type(data)}")

        bc_script.logger.add_info(f"Set {group_name} to: {data}")
        return save_data

    @dataclasses.dataclass
    class TalentOrbs(BaseParser):
        dict_key: str = "talent_orbs"

        orbs: dict[str, int] | None = None
        keep_previous: bool = True

        def apply(self, s: SaveFile):
            edit = bc_script.ctx.edit
            if edit is None:
                return

            if self.orbs is not None:
                orb_info_list = OrbInfoList.create(s)
                if orb_info_list is None:
                    bc_script.logger.add_error("Failed to create orb info list")
                    return
                all_orbs = orb_info_list.orb_info_list

                if not self.keep_previous:
                    s.talent_orbs.orbs.clear()
                    bc_script.logger.add_info("Cleared talent orbs")

                for talent, amount in self.orbs.items():
                    if talent.isdigit():
                        id = int(talent)
                        s.talent_orbs.set_orb(id, amount)
                        bc_script.logger.add_info(f"Set talent orb {id} to: {amount}")
                    else:
                        if talent == "all":
                            for orb in all_orbs:
                                s.talent_orbs.set_orb(orb.raw_orb_info.orb_id, amount)
                            bc_script.logger.add_info(
                                f"Set all talent orbs to: {amount}"
                            )
                        else:
                            parts = talent.split("-")
                            if not parts:
                                bc_script.logger.add_error(
                                    f"Invalid talent orb: {talent}"
                                )
                                continue

                            effect = parts[0]
                            grade = parts[1] if len(parts) > 1 else None
                            attribute = parts[2] if len(parts) > 2 else None

                            if not effect:
                                effect = None
                            if not grade:
                                grade = None
                            if not attribute:
                                attribute = None

                            for orb in all_orbs:
                                effect_id = orb.raw_orb_info.effect_id
                                effect_str = (
                                    orb.effect.lower().replace(" ", "_").split("_")[0]
                                )
                                if effect is not None:
                                    if effect.isdigit() and effect_id == int(effect):
                                        pass
                                    elif effect_str == effect:
                                        pass
                                    else:
                                        continue

                                grade_id = orb.raw_orb_info.grade_id
                                grade_str = (
                                    orb.grade.lower().replace(" ", "_").split("_")[0]
                                )

                                if grade is not None:
                                    if grade.isdigit() and grade_id == int(grade):
                                        pass
                                    elif grade_str == grade:
                                        pass
                                    else:
                                        continue

                                attribute_id = orb.raw_orb_info.attribute_id
                                attribute_str = (
                                    orb.attribute.lower()
                                    .replace(" ", "_")
                                    .split("_")[0]
                                )

                                if attribute is not None:
                                    if attribute.isdigit() and attribute_id == int(
                                        attribute
                                    ):
                                        pass
                                    elif attribute_str == attribute:
                                        pass
                                    else:
                                        continue

                                s.talent_orbs.set_orb(orb.raw_orb_info.orb_id, amount)
                                bc_script.logger.add_info(
                                    f"Set talent orb {orb.raw_orb_info.orb_id} to: {amount}"
                                )
