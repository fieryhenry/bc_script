import colorama


class Log:
    def __init__(
        self,
        show_warnings: bool = True,
        show_errors: bool = True,
        show_info: bool = False,
    ):
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.info: list[str] = []

        self.show_warnings = show_warnings
        self.show_errors = show_errors
        self.show_info = show_info

        colorama.init()

    def add_warning(self, warning: str):
        if self.show_warnings:
            print(f"{colorama.Fore.YELLOW}WARNING: {warning}{colorama.Style.RESET_ALL}")
        self.warnings.append(warning)

    def add_error(self, error: str):
        if self.show_errors:
            print(f"{colorama.Fore.RED}ERROR: {error}{colorama.Style.RESET_ALL}")
        self.errors.append(error)

    def add_info(self, info: str):
        if self.show_info:
            print(
                f"{colorama.Fore.LIGHTBLACK_EX}INFO: {info}{colorama.Style.RESET_ALL}"
            )
        self.info.append(info)

    def print(self):
        if self.show_errors:
            color = colorama.Fore.RED if len(self.errors) > 0 else colorama.Fore.GREEN
            print(
                f"{color}Finished with {len(self.errors)} errors{colorama.Style.RESET_ALL}"
            )
        if self.show_warnings:
            color = (
                colorama.Fore.YELLOW if len(self.warnings) > 0 else colorama.Fore.GREEN
            )
            print(
                f"{color}Finished with {len(self.warnings)} warnings{colorama.Style.RESET_ALL}"
            )
