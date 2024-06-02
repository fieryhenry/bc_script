from __future__ import annotations

import dataclasses
import inspect
from typing import Any, Callable, TypeVar

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
                inner = inner_classes.get(cls.list_cls.dict_key)
                if inner is not None:
                    clazz = inner.from_dict({cls.list_cls.dict_key: d})  # type: ignore
                    value = clazz
                else:
                    for key, value in d.items():  # type: ignore
                        if key not in args:
                            if inner is None:
                                bc_script.logger.add_warning(
                                    f"`{key}` is not a valid key for `{cls.__name__}`! Valid keys are: `{args}`"
                                )
                        else:
                            value = InputField(
                                key, value, cls.__dataclass_fields__[key].type  # type: ignore
                            ).value
                            d[key] = value
                    value = cls.list_cls(**d)  # type: ignore
                new_data_ls.append(value)

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
    def __init__(self, name: str, value: Any, type_str: str):
        self.name = name

        if isinstance(value, dict):
            for key, val in value.copy().items():
                key2 = key
                if str(key).startswith("__input__"):
                    key2 = self.gather_input(name, type(key).__name__, "", str(key))
                val2 = val
                if str(val).startswith("__input__"):
                    val2 = self.gather_input(name, type(val).__name__, "", str(val))
                del value[key]
                value[key2] = val2

        if isinstance(value, list):
            for i, val in enumerate(value):
                if str(val).startswith("__input__"):
                    vals = self.gather_input(
                        name, type(value).__name__, type(val).__name__, str(val)
                    )
                    if isinstance(vals, list):
                        value[i : len(vals)] = vals
                    else:
                        value[i] = val

        if str(value).startswith("__input__"):
            value = self.gather_input(name, type_str, "", str(value))

        self.value = value

        self.type = type_str

    def get_input_prompt(
        self,
        name: str,
        type_str: str,
        sub_type: str,
        key: str,
    ) -> tuple[str, Any, bool]:
        if key and key != "__input__":
            key = key.strip()[10:-1]
        else:
            key = ""

        typ = [t.strip() for t in type_str.split("|")]
        ty: Callable[[str], Any] = str

        if "int" in typ:
            ty = int
        elif "str" in typ:
            ty = str
        elif "list" in typ:
            if "int" in sub_type:
                ty = lambda x: [int(i) for i in x.split(",")]
            elif "str" in sub_type:
                ty = lambda x: [i for i in x.split(",")]

        else:
            raise ValueError(f"Unsupported type: {type_str}")

        can_be_none = "None" in typ

        input_str = f"Enter a value for {name}"
        if key:
            input_str += f" ({key})"
        if can_be_none:
            input_str += " (press enter to skip)"
        return input_str + ":", ty, can_be_none

    def gather_input(self, name: str, type_str: str, sub_type: str, key: str) -> Any:
        input_str, ty, can_be_none = self.get_input_prompt(
            name, type_str, sub_type, key
        )
        val = input(input_str)
        value = None
        if val or not can_be_none:
            try:
                value = ty(val)
            except ValueError:
                value = None
                bc_script.logger.add_error(
                    f"Invalid input for type: `{type_str}` for `{name}`"
                )

        return value


C = TypeVar("C", bound=BaseParser)
