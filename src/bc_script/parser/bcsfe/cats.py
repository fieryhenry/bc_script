from __future__ import annotations

import dataclasses


from bcsfe.core import SaveFile
import bcsfe

import bc_script
from bc_script.parser.parse import BaseParser


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
        set_current_forms: bool = True
        force_forms: bool = False

        claim_cat_guide: bool | None = None

        talents: Talents | None = None

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
                elif self.ids == "non_obtainable":
                    cats = s.cats.get_cats_non_obtainable(s) or []
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
                            cats.extend(s.cats.get_cats_gatya_banner(s, banner) or [])
                        else:
                            bc_script.logger.add_error(f"Invalid cat id: {id}")

                self.set_cats(s, cats)

        def set_cats(self, s: SaveFile, cats: list[bcsfe.core.Cat]):
            self.set_cat_forms(s, cats)

            for cat in cats:
                if self.unlock is not None:
                    cat.unlock(s) if self.unlock else cat.reset()
                    bc_script.logger.add_info(
                        f"{'Unlocked' if self.unlock else 'Removed'} cat: {cat.id}"
                    )

                self.upgrade_cat(cat, s)

                if self.claim_cat_guide is not None:
                    cat.catguide_collected = self.claim_cat_guide
                    bc_script.logger.add_info(
                        f"{'Claimed' if self.claim_cat_guide else 'Removed'} cat guide for cat: {cat.id}"
                    )

            if self.talents is not None:
                self.talents.apply(s, cats)

        def set_cat_forms(self, s: SaveFile, cats: list[bcsfe.core.Cat]):
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

        def upgrade_cat(self, cat: bcsfe.core.Cat, s: SaveFile):
            if self.upgrade is not None:
                if len(self.upgrade) != 2:
                    bc_script.logger.add_error(f"Invalid upgrade data: {self.upgrade}")

                upgrade_base = self.get_base(cat, s)
                upgrade_plus = self.get_plus(cat, s)

                if upgrade_base is None or upgrade_plus is None:
                    return

                upgrade = bcsfe.core.Upgrade(plus=upgrade_plus, base=upgrade_base - 1)
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

            if isinstance(self.upgrade[0], str) and not str(self.upgrade[0]).isdigit():
                if self.upgrade[0] == "max":
                    upgrade_base = powerup.get_max_possible_base()
                else:
                    bc_script.logger.add_error(
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

            if isinstance(self.upgrade[1], str) and not str(self.upgrade[1]).isdigit():
                if self.upgrade[1] == "max":
                    upgrade_plus = powerup.get_max_possible_plus()
                else:
                    bc_script.logger.add_error(
                        f"Invalid upgrade plus: {self.upgrade[1]}"
                    )
                    return None
            else:
                upgrade_plus = int(self.upgrade[1])

            return upgrade_plus

        @dataclasses.dataclass
        class Talents(BaseParser):
            dict_key: str = "talents"

            talents: dict[str, str | int] | None = None
            keep_existing: bool = True

            def apply(self, s: SaveFile, cats: list[bcsfe.core.Cat]):
                edit = bc_script.ctx.edit
                if edit is None:
                    return

                if self.talents is None:
                    return

                talent_data = s.cats.read_talent_data(s)
                if talent_data is None:
                    bc_script.logger.add_warning("Failed to read talent data")
                    return

                for cat in cats:
                    if cat.talents is None:
                        if len(cats) < 20:  # Only log if there are few cats
                            bc_script.logger.add_warning(
                                f"Failed to read talents for cat: {cat.id}"
                            )
                        continue

                    if not self.keep_existing:
                        for talent in cat.talents:
                            talent.level = 0

                    cat_talent_data = talent_data.get_cat_talents(cat)
                    if cat_talent_data is None:
                        bc_script.logger.add_warning(
                            f"Failed to read talent data for cat: {cat.id}"
                        )
                        continue

                    talent_names, max_levels, _, ids = cat_talent_data

                    talent_ids: list[tuple[int, str]] = []

                    for talent_id, level in self.talents.items():
                        if talent_id == "all":
                            talent_ids = [(i, str(level)) for i in range(len(ids))]
                            break
                        if not talent_id.isdigit():
                            bc_script.logger.add_error(
                                f"Invalid talent id: {talent_id}"
                            )
                            continue
                        talent_ids.append((int(talent_id), str(level)))

                    for talent_id, level in talent_ids:
                        id = ids[talent_id]
                        name = talent_names[talent_id]
                        max_level = max_levels[talent_id]
                        talent = cat.get_talent_from_id(id)
                        if talent is None:
                            bc_script.logger.add_warning(
                                f"Failed to find talent with id: {talent_id}"
                            )
                            continue

                        if max_level == 0:
                            max_level = 1

                        if level == "max":
                            lv = max_level
                        else:
                            if not level.isdigit():
                                bc_script.logger.add_error(
                                    f"Invalid talent level: {level}"
                                )
                                continue
                            lv = int(level)

                        if lv > max_level:
                            bc_script.logger.add_warning(
                                f"Talent level exceeds max level: {name} ({lv} > {max_level})"
                            )

                        talent.level = lv

                        bc_script.logger.add_info(
                            f"Set talent level for cat: {cat.id} talent: {name} to {lv}"
                        )

    list_cls = CatEdit
