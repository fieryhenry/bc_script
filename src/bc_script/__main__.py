import argparse
import os

import bcsfe
import toml

import bc_script


def load_args():
    parser = argparse.ArgumentParser(
        prog="bc_script",
        description="Battle Cats Scripting",
    )
    parser.add_argument(
        "script_path",
        type=str,
        help="path to the script .toml file",
    )
    parser.add_argument(
        "-i",
        dest="in_save_path",
        default=None,
        type=str,
        help="path to the input save file. overrides the load section in the script",
    )
    parser.add_argument(
        "-o",
        dest="out_save_path",
        default=None,
        type=str,
        help="path to the output save file. overrides the save section in the script",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {bc_script.__version__}",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="show debug messages",
    )

    args = parser.parse_args()
    if args.out_save_path is None:
        args.out_save_path = args.in_save_path
    return args


def main():
    args = load_args()
    if not os.path.exists(args.script_path):
        print(f"File not found: {args.script_path}")
        return
    with open(args.script_path, "r") as f:
        data = toml.load(f)

    in_path = args.in_save_path
    if in_path is not None:
        in_path = bcsfe.core.Path(in_path)

    out_path = args.out_save_path
    if out_path is not None:
        out_path = bcsfe.core.Path(out_path)

    bc_script.logger.show_info = args.debug

    bc_script.parser.parse.do(data, in_path, out_path)

    bc_script.logger.print()


if __name__ == "__main__":
    main()
