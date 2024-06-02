from __future__ import annotations

import dataclasses
import typing

from bcsfe.core import CountryCode, GameVersion, Path, SaveFile, ServerHandler, JsonFile

import bc_script
from bc_script.parser.parse import BaseParser

from typeguard import typechecked


@dataclasses.dataclass
class Load(BaseParser):
    error_on_not_found = True
    dict_key: str = "load"

    country_code: str | None = None
    path: str | None = None

    file: File | None = None
    transfer: Transfer | None = None
    adb: Adb | None = None
    json: Json | None = None

    @typechecked
    def __new__(
        cls,
        country_code: str | None = None,
        path: str | None = None,
        **kwargs: typing.Any,
    ):
        return super().__new__(cls)

    def load(self) -> SaveFile | None:
        bc_script.logger.add_info(f"Loading save file")
        if self.file is not None:
            return self.file.load()
        if self.transfer is not None:
            return self.transfer.load()
        if self.adb is not None:
            return self.adb.load()
        if self.json is not None:
            return self.json.load()
        return None

    def get_cc(self) -> CountryCode | None:
        if self.country_code is None:
            return None
        return CountryCode.from_code(self.country_code)

    def get_path(self) -> Path | None:
        if self.path is None:
            return None

        return Path(self.path)

    @dataclasses.dataclass
    class File(BaseParser):
        dict_key: str = "file"

        def load(self) -> SaveFile | None:
            load = bc_script.ctx.load
            if load is None:
                return None
            path = load.get_path()
            if path is None:
                return None
            save_file = SaveFile(path.read())
            return save_file

    @dataclasses.dataclass
    class Transfer(BaseParser):
        transfer_code: str = dataclasses.field(kw_only=True)
        confirmation_code: str = dataclasses.field(kw_only=True)
        dict_key: str = "transfer"

        @typechecked
        def __new__(
            cls, transfer_code: str, confirmation_code: str, **kwargs: typing.Any
        ):
            return super().__new__(cls)

        def load(self) -> SaveFile | None:
            ctx = bc_script.ctx
            if ctx.load is None:
                return None
            cc = ctx.load.get_cc()
            if cc is None:
                return None

            gv = GameVersion.from_string("12.2.0")
            bc_script.logger.add_info(
                f"Dowloading save file with codes: {self.transfer_code}, {self.confirmation_code}"
            )
            server_handler, res = ServerHandler.from_codes(
                self.transfer_code, self.confirmation_code, cc, gv
            )
            if res is not None or server_handler is None:
                bc_script.logger.add_error(
                    f"Failed to download save. Transfer codes / country code is probably incorrect"
                )

                return None
            bc_script.logger.add_info("Save file downloaded")
            return server_handler.save_file

    @dataclasses.dataclass
    class Adb(BaseParser):
        dict_key: str = "adb"
        device: str | None = None
        package_name: str | None = None

        @typechecked
        def __new__(
            cls,
            device: str | None = None,
            package_name: str | None = None,
            **kwargs: typing.Any,
        ):
            return super().__new__(cls)

        def load(self) -> SaveFile | None:
            ctx = bc_script.ctx
            load = ctx.load
            if load is None:
                return

            adb_handler = bc_script.setup_adb(self.device, self.package_name)
            if adb_handler is None:
                return

            bc_script.logger.add_info("Pulling save file from device")
            path, res = adb_handler.save_locally(load.get_path())

            if path is None:
                bc_script.logger.add_error(res.result)
                return None

            save_file = SaveFile(path.read(), package_name=self.package_name)
            save_file.used_storage = True

            bc_script.logger.add_info("Save file pulled from device")

            return save_file

    @dataclasses.dataclass
    class Json(BaseParser):
        dict_key: str = "json"
        path: str = dataclasses.field(kw_only=True)

        @typechecked
        def __new__(cls, path: str, **kwargs: typing.Any):
            return super().__new__(cls)

        def load(self) -> SaveFile | None:
            load = bc_script.ctx.load
            if load is None:
                return None
            save_path = load.get_path()

            json_path = Path(self.path)
            if not json_path.exists():
                bc_script.logger.add_error(f"Json file not found: {json_path}")
                return None

            json = JsonFile.from_path(json_path)

            save_file = SaveFile.from_dict(json.to_object())
            if save_path is not None:
                save_file.save_path = save_path
                save_file.to_file(save_path)

            bc_script.logger.add_info(f"Loaded save file from json: {json_path}")
            return save_file
