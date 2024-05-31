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

    def add_warning(self, warning: str):
        if self.show_warnings:
            print(f"WARNING: {warning}")
        self.warnings.append(warning)

    def add_error(self, error: str):
        if self.show_errors:
            print(f"ERROR: {error}")
        self.errors.append(error)

    def add_info(self, info: str):
        if self.show_info:
            print(f"INFO: {info}")
        self.info.append(info)

    def print(self):
        if self.show_errors:
            print(f"Finished with {len(self.errors)} errors")
        if self.show_warnings:
            print(f"Finished with {len(self.warnings)} warnings")
