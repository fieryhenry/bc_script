from __future__ import annotations

import dataclasses


from bcsfe.core import SaveFile
import bcsfe

import bc_script
from bc_script.parser.parse import BaseParser


@dataclasses.dataclass
class SpecialSkills(BaseParser):
    dict_key: str = "special_skills"

    special_skills: list[SpecialSkill] | None = None

    def apply(self, s: SaveFile):
        edit = bc_script.ctx.edit
        if edit is None:
            return

        if self.special_skills is not None:
            for special_skill in self.special_skills:
                special_skill.apply(s)

        s.max_rank_up_sale()

    @dataclasses.dataclass
    class SpecialSkill(BaseParser):
        dict_key: str = "special_skill"

        ids: list[int | str] | None | str = None
        upgrade: list[int | str] | None = None
        upgrade_base: int | str | None = None
        upgrade_plus: int | str | None = None

        def apply(self, s: SaveFile):
            edit = bc_script.ctx.edit
            if edit is None:
                return

            if self.ids is None:
                return

            skills: list[tuple[int, bcsfe.core.SpecialSkill]] = []

            if self.ids == "all":
                for i, skill in enumerate(s.special_skills.get_valid_skills()):
                    skills.append((i, skill))
            else:
                for id in self.ids:
                    if not str(id).isdigit():
                        bc_script.logger.add_error(f"Invalid special skill id: {id}")
                        continue

                    skill = s.special_skills.get_from_id(int(id))
                    if skill is not None:
                        skills.append((int(id), skill))
                    else:
                        bc_script.logger.add_error(f"Special skill not found: {id}")

            for id, skill in skills:
                self.upgrade_skill(id, skill, s)

        def upgrade_skill(self, id: int, skill: bcsfe.core.SpecialSkill, s: SaveFile):
            if self.upgrade is not None:
                if len(self.upgrade) != 2:
                    bc_script.logger.add_error(f"Invalid upgrade data: {self.upgrade}")

                upgrade_base = self.get_base(id, s, self.upgrade[0])
                upgrade_plus = self.get_plus(id, s, self.upgrade[1])

                if upgrade_base is None or upgrade_plus is None:
                    return

                upgrade = bcsfe.core.Upgrade(plus=upgrade_plus, base=upgrade_base - 1)
                skill.set_upgrade(upgrade)
                bc_script.logger.add_info(
                    f"Set upgrade for skill: {id} to {upgrade.base+1}+{upgrade.plus}"
                )

            if self.upgrade_base is not None:
                upgrade_base = self.get_base(id, s, self.upgrade_base)
                if upgrade_base is None:
                    return
                upgrade = skill.upgrade
                upgrade.base = upgrade_base - 1
                skill.set_upgrade(upgrade)
                bc_script.logger.add_info(
                    f"Set upgrade base for skill: {id} to {upgrade.base+1}"
                )

            if self.upgrade_plus is not None:
                upgrade_plus = self.get_plus(id, s, self.upgrade_plus)
                if upgrade_plus is None:
                    return
                upgrade = skill.upgrade
                upgrade.plus = upgrade_plus
                skill.set_upgrade(upgrade)
                bc_script.logger.add_info(
                    f"Set upgrade plus for skill: {id} to +{upgrade.plus}"
                )

        def get_base(self, id: int, s: SaveFile, level: str | int):
            ability_data = bcsfe.core.core_data.get_ability_data(s)
            if ability_data.ability_data is None:
                return
            ability = ability_data.get_ability_data_item(id)
            if ability is None:
                return

            if isinstance(level, str) and not str(level).isdigit():
                if level == "max":
                    upgrade_base = ability.max_base_level
                else:
                    bc_script.logger.add_error(f"Invalid upgrade base: {level}")
                    return None
            else:
                upgrade_base = int(level)

            return upgrade_base

        def get_plus(self, id: int, s: SaveFile, level: str | int):
            ability_data = bcsfe.core.core_data.get_ability_data(s)
            if ability_data.ability_data is None:
                return
            ability = ability_data.get_ability_data_item(id)
            if ability is None:
                return

            if isinstance(level, str) and not str(level).isdigit():
                if level == "max":
                    upgrade_plus = ability.max_plus_level
                else:
                    bc_script.logger.add_error(f"Invalid upgrade plus: {level}")
                    return None
            else:
                upgrade_plus = int(level)

            return upgrade_plus

    list_cls = SpecialSkill
