# AltStore Source for Enmity
![Icons](https://skillicons.dev/icons?i=py,githubactions,github)

[![wakatime](https://wakatime.com/badge/github/burritosoftware/enmity-altsource.svg)](https://wakatime.com/badge/github/burritosoftware/enmity-altsource) [![Last updated](https://img.shields.io/github/last-commit/burritosoftware/enmity-altsource/pages?logo=github&label=last%20updated)](https://github.com/burritosoftware/enmity-altsource/commits/pages/) ![Update check/source generation)](https://img.shields.io/github/actions/workflow/status/burritosoftware/enmity-altsource/create.yml?logo=github&label=update%20check%2Fsource%20generation)

---

## How this works
This repository checks every hour for new builds of Enmity at [enmity-mod/tweak](https://github.com/enmity-mod/tweak/releases).  
If one exists, the AltStore source in the `pages` branch will be updated to the latest version.

## Installation
Tap below to open AltStore and add this source. Not working? Add `https://enmity.burrito.software/apps.json` to AltStore.

[![Add to AltStore](https://taidums.are-really.cool/9nj3vv5.png)](https://enmity.burrito.software)

## Manual Setup
This code can be run without GitHub actions.  
Tested on Windows 11 and `ubuntu-latest` Actions runner.

1. Make sure you have Python installed.
2. Install/upgrade dependencies:
  ```
  pip install -U -r requirements.txt
  ```
3. Duplicate `.env-example` to `.env`.
  ```
  cp .env-example .env
  ```
3. Run `generate.py`.
  ```
  python3 generate.py
  ```
4. The AltStore source file will be located, by default, in `out/apps.json`. A file to compare and track new versions will be, by default, in `cache/lastGenerated.json`. You can adjust these parameters in the `.env` file.