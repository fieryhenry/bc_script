from __future__ import annotations

__version__ = "0.0.1"


import bcsfe

from bc_script import log, parser


class Ctx:
    def __init__(self):
        self.pkg: parser.pkg.Pkg | None = None
        self.info: parser.info.Info | None = None
        self.load: parser.bcsfe.load.Load | None = None
        self.edit: parser.bcsfe.edit.Edit | None = None
        self.save: parser.bcsfe.save.Save | None = None


logger = log.Log()
ctx = Ctx()


def setup_adb(
    device: str | None,
    package_name: str | None,
    save: bcsfe.core.SaveFile | None = None,
):
    adb_handler = bcsfe.core.AdbHandler()
    if device is not None:
        adb_handler.set_device(device)
    else:
        devices = adb_handler.get_connected_devices()
        if not devices:
            logger.add_error("There are no devices connected with adb")
            return
        if len(devices) > 1:
            logger.add_error(
                f"There are multiple devices found. Please disconnect some / specify device id. {devices}"
            )
            return
        adb_handler.set_device(devices[0])

    if package_name is not None:
        adb_handler.set_package_name(package_name)
    else:
        if save is not None and save.used_storage and save.package_name is not None:
            adb_handler.set_package_name(save.package_name)
        else:
            package_names = adb_handler.get_battlecats_packages()
            if not package_names:
                logger.add_error("There are no game versions installed")
            if len(package_names) > 1:
                logger.add_error(
                    f"There are multiple game versions installed. Please specifiy package name. {package_names}"
                )
            adb_handler.set_package_name(package_names[0])

    return adb_handler
