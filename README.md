# Resolution Changer

Resolution Changer temporarily changes the Windows display resolution so you
can run an older game that requires a different resolution. When the game
closes, the program restores the computer's previous display resolution.

## Usage

Run the following command from Command Prompt, replacing `{width}`, `{height}`,
and `{path to the game}` with the desired values:

```text
python reschanger.py -w {width} -h {height} "{path to the game}"
```

For example:

```text
python reschanger.py -w 1024 -h 768 "C:\Games\game.exe"
```

Use the command as the target of a Windows shortcut to launch the game with the
desired resolution. Include the correct paths to `reschanger.py` and the game
executable. Put paths in quotation marks if they contain spaces.
