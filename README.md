# AWS Glue Manager
[![License](https://img.shields.io/badge/license-GPL%20v3-9ac813)](COPYING)

    AWS Glue Manager - Python and Qt5 based application to list, filter,
    read the details of AWS Glue jobs and workflows.

    Copyright (C) 2021  Giacomo Furlan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Icons by [Feathericons](https://github.com/feathericons/feather)

## Compiling

### Prerequisites

- pipenv
- python 3.9

### Generic method

You can create a redistributable binary using pyinstaller

```bash
pipenv run pyinstaller --name "AWSGlueManager" --windowed --onefile main.py
```

After that, the `ui/icons` folder must be copied into `dist/ui`.

### Linux, OSX

You can compile the project using `make`.
```bash
make dist
```

Make targets:
- `dist`: create a redistributable binary
  - `build-dist`: execute pyinstaller
  - `copy-icons`: copy the icons in the dist folder
- `test`: run the test suite
- `clean`: remove the dist folder
- `all` (default): execute `clean`, `test`, `dist`

### Windows
 Work in progress. For now, execute the following commands:

```
pipenv run pip install pywin32-ctypes
pipenv run pip install pefile
pipenv run pyinstaller --name "AWSGlueManager" --windowed --onefile main.py
xcopy /i ui\icons dist\ui\icons
```

## Executing

### Executing flags
You can add the following flags to the application's call:
- `-d`, `--debug`: enable the debug logger with debug level
- `-i`, `--info`: enable the debug logger with info level

### From sources
```
pipenv run python main.py [flags]
```

### From binary
```
./AWSGlueManager [flags]
```
