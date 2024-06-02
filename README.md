# BC Script

A scripting system for the mobile game The Battle Cats, integrates with
[bcsfe](<https://github.com/fieryhenry/BCSFE_Python>) only at the moment.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/M4M53M4MN)

## Features

- Load save from file, adb and transfer codes
- Save to file, adb and transfer codes
- Modify save data

## Installation

1. Install [bcsfe](https://github.com/fieryhenry/BCSFE-Python/tree/3.0.0?tab=readme-ov-file#install-from-source)
3.0.0 from source
2. Run the following command in the terminal:

```bash
git clone https://github.com/fieryhenry/bc_script.git
cd bc_script
pip install -e .
python -m bc_script
```

You may need to use `py` or `python3` instead of `python` in the commands above.

## Usage

```bash
python -m bc_script --help
```

## Script files

Scripts are written in toml format. You need to specify the path to the script
file when running the module.

Note that you can replace most values with the string `__input__` to prompt the
user for input.

e.g

```toml
[load]
path = "__input__"

[edit.basic_items]
catfood = "__input__"
```

```toml
[pkg] # specify the package name and version used
schema = "bcsfe" # only bcsfe is supported atm, tbcml may be added in the future
version = "3.0.0" 

[info] # specify the script details
name = "Example script"
description = "An example script"
author = "fieryhenry"
version = "1.0.0"

[load] # specify the main save data load options
country_code = "en" # the country code of the save data valid options are "en", "jp", "kr", "tw" (optional)
path = "path/to/save/file" # the path to the save file or the path you want to save the save file to

[load.file] # specify the options to enable loading from a file (optional)

[load.adb] # specify the options to enable loading from adb (optional)
device = "emulator-5554" # the device id of the adb device if multiple devices are connected (optional)
package_name = "jp.co.ponos.battlecatsen" # the package name of the game if multiple games are installed (optional)

[load.transfer] # specify the options to enable loading from a transfer code (optional)
transfer_code = "abcdef012" # the transfer code to load from
confirmation_code = "01234" # the confirmation code to load from

[edit] # specify the main save data edit options (optional)
managed_items = ["catfood", "rareticket", "platinumticket", "legendticket"] # the items to send to the game servers to prevent bans, defaults to the above if not specified
forced_locale = "en" # the locale to force the editor to use, valid options are "en", "jp", "kr", "tw" (optional)

[edit.basic_items] # specify the basic items to edit (optional)
catfood = 10000 
xp = 1000000
normal_tickets = 10
rare_tickets = 10
platinum_tickets = 9
legend_tickets = 4
platinum_shards = 10
np = 9999
leadership = 9999
battle_items = [1, 10, 9999, 1002, 9999, 0]
# alternatively, you can use the following format
# battle_items = {0 = 1, 1 = 10, 2 = 9999, 3 = 1002, 4 = 9999, 5 = 0}
# the keys are the indexes of the battle items, the values are the quantities
# if a key is missing, the quantity is not changed
catamins = [0, 1, 2]
catseyes = [0, 1, 2, 3, 4]
catfruit = {0 = 10, 3 = 50}

[edit.basic_items.talent_orbs]
orbs = {0 = 10, "massive-s-alien" = 5, "-d-red" = 3, "all" = 1, "strong-a-" = 2}
# the above are examples of the different formats you can use.
# Note that the names of the orbs follow the same format as the names in the
# game files. So if you are using jp, the names will be in jp, etc.
keep_previous = false # whether to keep the previous orbs or not. Defaults to true if not specified

[[edit.cats]] # specify the cat edit options (optional)
ids = [0, 1, 2] # the ids of the cats to edit:
# ids = "all" to edit all cats
# ids = "obtainable" to edit all obtainable cats
# ids = "unlocked" to edit all unlocked cats
# ids = "non_unlocked" to edit all non unlocked cats
# ids = "non_obtainable" to edit all non obtainable cats
# ids = ["rarity-0", "rarity-1"] to edit all cats with the specified rarity
# 0 = normal, 1 = special, 2 = rare, 3 = super rare, 4 = uber super rare, 5 = legend rare
# ids = ["banner-512", "banner-513"] to edit all cats in a specific gatya banner

unlock = true # whether to unlock or remove the cats
upgrade = [10, 20] # the levels to upgrade the cats to (base, +)
# upgrade = ["max", 20] to upgrade the cats to the max base level
# upgrade = [10, "max"] to upgrade the cats to the max + level
# upgrade = ["max", "max"] to upgrade the cats to the max base and + levels
upgrade_base = 10 # just upgrade the base level
upgrade_plus = 20 # just upgrade the + level
true_form = true # whether to true form or un true form the cats
ultra_form = true # whether to ultra form or un ultra form the cats
set_current_forms = true # whether to set the current forms of the cats to the specified forms, e.g if a cat's true form is unlocked, set the current form of the cat to the true form
force_forms = false # whether to force true or ultra forms on cats that can't be true or ultra formed
claim_cat_guide = true # whether to claim the cat guide for the cats. does not give cat guide rewards

[[edit.cats]]
ids = [0, 1, 2] # you can specify multiple cat edit options for different cat sets
unlock = false # with different options

[edit.cats.talents]
talents = {0=10, 1=5, 2="max"} # the talents to set for the cats
# 0 = first talent, 1 = second talent, 2 = third talent, etc
# the values are the levels of the talents
# "max" = max level of the talent
# you can also say 
# talents = {all = "max"} to set all talents to max level

keep_existing = false # whether to keep the existing talents or not. Defaults to true if not specified


[save]
path = "path/to/save/file" # the path you want to save the save file to
upload_managed_items = true # whether to upload the managed items to the game servers to prevent bans

[save.file] # specify the options to enable saving to a file (optional)

[save.adb] # specify the options to enable saving to adb (optional)
device = "emulator-5554" # the device id of the adb device if multiple devices are connected (optional)
package_name = "jp.co.ponos.battlecatsen" # the package name of the game if multiple games are installed (optional)
rerun = true # whether to rerun the game after saving

[save.transfer] # specify the options to enable saving to a transfer code (optional)

```

## TODO

most of these are features in bcsfe that need to be added to bc_script

- Special skills
- Init empty save
- Convert save versions
- Load and save to json
- Add scheme items
- Add labyrinth medals
- All level stuff
- All gamatoto stuff
- All account related stuff
- All gatya related stuff
- All fixes
- All other stuff
- Add support for tbcml
