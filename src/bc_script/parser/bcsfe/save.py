from __future__ import annotations

import dataclasses
import typing

from bcsfe.core import BackupMetaData, Path, SaveFile, ServerHandler, JsonFile

import bc_script
from bc_script.parser.parse import BaseParser

from typeguard import typechecked


@dataclasses.dataclass
class Save(BaseParser):
    dict_key: str = "save"

    path: str | None = None
    upload_managed_items: bool = True

    file: File | None = None
    transfer: Transfer | None = None
    adb: Adb | None = None
    json: Json | None = None

    @typechecked
    def __new__(
        cls,
        path: str | None = None,
        upload_managed_items: bool = True,
        **kwargs: typing.Any,
    ):
        return super().__new__(cls)

    def save(self, s: SaveFile):
        bc_script.logger.add_info("Saving save file")
        self.check_managed_items(s)
        if self.file is not None:
            self.file.save(s)
        if self.transfer is not None:
            self.transfer.save(s)
        if self.adb is not None:
            self.adb.save(s)
        if self.json is not None:
            self.json.save(s)

    def check_managed_items(self, s: SaveFile):
        if not self.upload_managed_items:
            return
        managed_items = BackupMetaData(s).get_managed_items()
        if not managed_items:
            return

        bc_script.logger.add_info("Uploading managed items")
        server_handler = ServerHandler(s, print=False)
        if not server_handler.upload_meta_data():
            bc_script.logger.add_warning("Failed to upload managed items")

    def get_path(self) -> Path | None:
        if self.path is None:
            return None
        return Path(self.path)

    @dataclasses.dataclass
    class File(BaseParser):
        dict_key: str = "file"

        def save(self, s: SaveFile):
            sv = bc_script.ctx.save
            if sv is None:
                return
            path = sv.get_path()
            if path is None:
                path = s.save_path
            if path is None:
                return

            bc_script.logger.add_info(f"Saving to: {path}")

            s.to_file(path)

    @dataclasses.dataclass
    class Transfer(BaseParser):
        dict_key: str = "transfer"

        def save(self, s: SaveFile):
            sv = bc_script.ctx.save
            if sv is None:
                return

            bc_script.logger.add_info("Uploading save file to server")
            codes = ServerHandler(s, print=False).get_codes(sv.upload_managed_items)
            if codes is None:
                return

            path = sv.get_path()
            if path is None:
                path = s.save_path
            if path is None:
                return
            s.to_file(path)

            print(f"Transfer Code: {codes[0]}")
            print(f"Confirmation Code: {codes[1]}")

    @dataclasses.dataclass
    class Adb(BaseParser):
        dict_key: str = "adb"
        rerun: bool = False
        device: str | None = None
        package_name: str | None = None

        @typechecked
        def __new__(
            cls,
            rerun: bool = False,
            device: str | None = None,
            package_name: str | None = None,
            **kwargs: typing.Any,
        ):
            return super().__new__(cls)

        def save(self, s: SaveFile):
            ctx = bc_script.ctx
            save = ctx.save
            if save is None:
                return

            adb_handler = bc_script.setup_adb(self.device, self.package_name, s)
            if adb_handler is None:
                return

            path = save.get_path()
            if path is None:
                path = s.save_path
            if path is None:
                return

            s.to_file(path)

            bc_script.logger.add_info("Pushing save file to device")

            result = adb_handler.load_battlecats_save(path)
            if not result.success:
                bc_script.logger.add_error(result.result)

            bc_script.logger.add_info("Save file pushed to device")

            if self.rerun:
                bc_script.logger.add_info("Rerunning game")
                adb_handler.rerun_game()
                bc_script.logger.add_info("Game rerun")

    @dataclasses.dataclass
    class Json(BaseParser):
        dict_key: str = "json"
        path: str | None = None

        @typechecked
        def __new__(cls, path: str | None = None, **kwargs: typing.Any):
            return super().__new__(cls)

        def save(self, s: SaveFile):
            sv = bc_script.ctx.save
            if sv is None:
                return
            path = self.path
            if path is None:
                path = sv.get_path()
            else:
                path = Path(path)
            if path is None:
                return

            bc_script.logger.add_info(f"Saving to: {path}")

            json_data = s.to_dict()
            json = JsonFile.from_object(json_data)
            json.to_file(path)
