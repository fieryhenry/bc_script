from __future__ import annotations

import dataclasses
import inspect
from typing import Any, TypeVar

import bcsfe

import bc_script


def parse(data: dict[str, Any]):
    ctx = bc_script.ctx
    pkg = bc_script.parser.pkg.Pkg.from_dict(data)
    ctx.pkg = pkg
    info = bc_script.parser.info.Info.from_dict(data)
    ctx.info = info

    if pkg.schema == "bcsfe":
        load = bc_script.parser.bcsfe.load.Load.from_dict(data)
        ctx.load = load
        edit = bc_script.parser.bcsfe.edit.Edit.from_dict(data)
        ctx.edit = edit
        save = bc_script.parser.bcsfe.save.Save.from_dict(data)
        ctx.save = save

    return ctx


def load_save(path: bcsfe.core.Path):
    save = bcsfe.core.SaveFile(path.read())
    return save


def do(
    script_data: dict[str, Any],
    in_path: bcsfe.core.Path | None,
    out_path: bcsfe.core.Path | None,
):
    ctx = parse(script_data)

    if in_path is not None:
        save = load_save(in_path)
    else:
        if ctx.load is None:
            bc_script.logger.add_error("Failed to load any save file")
            return
        sv = ctx.load.load()
        if sv is None:
            bc_script.logger.add_error("Failed to load any save file")
            return
        save = sv
    if ctx.edit is not None:
        ctx.edit.apply(save)

    save_action = ctx.save
    if save_action is None:
        if out_path is None:
            return
        save.to_file(out_path)
    else:
        save_action.save(save)


@dataclasses.dataclass
class BaseParser:
    dict_key: str = dataclasses.field(kw_only=True, default="", repr=False)
    warn_on_not_found: bool = dataclasses.field(kw_only=True, default=False, repr=False)
    error_on_not_found: bool = dataclasses.field(
        kw_only=True, default=False, repr=False
    )
    list_cls: type[BaseParser] | None = dataclasses.field(
        kw_only=True, default=None, repr=False
    )
    subclasses: list[type[BaseParser]] | None = dataclasses.field(
        kw_only=True, default=None
    )

    @classmethod
    def from_dict(cls: type[C], data: dict[str, dict[str, Any]]) -> C:
        dt: dict[str, Any] | list[dict[str, Any]] | None = data.get(cls.dict_key)
        if dt is None:
            if cls.warn_on_not_found:
                bc_script.logger.add_warning(
                    f"{cls.dict_key} key was not found in script"
                )
            if cls.error_on_not_found:
                bc_script.logger.add_error(
                    f"{cls.dict_key} key was not found in script"
                )
            dt = {}

        args = list(cls.__dataclass_fields__.keys())

        for key in BaseParser.__dataclass_fields__.keys():
            args.remove(key)

        inner_classes = cls.get_inner_classes()

        if isinstance(dt, list):
            if cls.list_cls is None:
                raise ValueError("list_cls must be set for list types")
            new_data_ls: list[Any] = []
            for d in dt:
                for key, value in d.items():  # type: ignore
                    inner = inner_classes.get(cls.list_cls.dict_key)
                    if inner is not None:
                        clazz = inner.from_dict({cls.list_cls.dict_key: d})  # type: ignore
                        value = clazz
                    if key not in args:
                        if inner is None:
                            bc_script.logger.add_warning(
                                f"`{key}` is not a valid key for `{cls.__name__}`! Valid keys are: `{args}`"
                            )
                    else:
                        value = InputField(
                            key, value, cls.__dataclass_fields__[key].type  # type: ignore
                        ).value
                        new_data_ls[key] = value
                new_data_ls.append(value)  # type: ignore

            kwargs = {cls.dict_key: new_data_ls}

            c = cls(**kwargs)  # type: ignore
            return c

        new_data: dict[str, Any] = {}
        for key, value in dt.items():
            inner = inner_classes.get(key)
            if inner is not None:
                clazz = inner.from_dict(dt)
                value = clazz
            if key not in args:
                if inner is None:
                    bc_script.logger.add_warning(
                        f"`{key}` is not a valid key for `{cls.__name__}`! Valid keys are: `{args}`"
                    )
            else:
                value = InputField(key, value, cls.__dataclass_fields__[key].type).value
                new_data[key] = value

        return cls(**new_data)

    @classmethod
    def get_inner_classes(cls):
        classes = {
            cls_attribute.dict_key: cls_attribute
            for cls_attribute in cls.__dict__.values()
            if inspect.isclass(cls_attribute) and issubclass(cls_attribute, BaseParser)
        }
        classes.update({sub.dict_key: sub for sub in cls.subclasses or []})
        return classes


class InputField:
    def __init__(self, name: str, value: Any, type: str):
        self.name = name

        if value == "__input__":
            typ = [t.strip() for t in type.split("|")]
            if "int" in typ:
                ty = int
            elif "str" in typ:
                ty = str
            else:
                raise ValueError(f"Unsupported type: {type}")

            can_be_none = "None" in typ

            input_str = f"Enter a value for {name}"
            if can_be_none:
                input_str += " (press enter to skip)"
            val = input(input_str + ":")
            value = None
            if val or not can_be_none:
                try:
                    value = ty(val)
                except ValueError:
                    value = None
                    bc_script.logger.add_error(
                        f"Invalid input for type: `{type}` for `{name}`"
                    )

        self.value = value

        self.type = type


C = TypeVar("C", bound=BaseParser)
