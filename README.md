# Car Ralling

Car Ralling is a single-player, top-down arcade driving game built with Python and Pygame. It combines a 20-stage career, changing seasonal biomes, persistent progression, vehicle customization and Windows packaging in a compact project.

## Highlights

- 20-stage story career with a gradual difficulty curve
- Spring, summer, autumn, winter, desert, city and night environments
- Environment-specific mechanics: rain, fog, ice drift, heat and crossing sheep
- Persistent high score, gold, jokers, selected vehicle, color and pattern
- Five vehicle classes and eight unlockable paint patterns
- Fuel, shield, turbo and reward pickups
- Keyboard and mouse-driven menus, garage, settings and pause screens
- Resolution options, fullscreen support, sound effects and Windows save storage
- One-command Windows `.exe` build

## Controls

| Action | Input |
|---|---|
| Drive | `WASD` or arrow keys |
| Pause | `P` or `Esc` |
| Garage | `G` or the on-screen button |
| Fullscreen | `F11` |
| Menu interaction | Mouse |

## Run from source

Python 3.12 is recommended.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python car_ralling.py
```

## Build for Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

The packaged game is created at `dist\CarRalling.exe`. Save data is stored separately at:

```text
%LOCALAPPDATA%\CarRalling\savegame.json
```

This keeps player progress intact when the executable is replaced with a newer build.

## Tests

```powershell
$env:SDL_VIDEODRIVER="dummy"
$env:SDL_AUDIODRIVER="dummy"
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs the same logic tests on every push and pull request.

## Project structure

```text
car_ralling.py          Main game and UI
assets/vehicles/        Vehicle sprites
assets/audio/           Sound effects and asset license
tests/                  Progression and gameplay logic tests
build_windows.ps1       Reproducible Windows build script
version_info.txt        Windows executable metadata
```

## Credits

- Game design and programming: YağmurZ
- Audio effects: Kenney assets, released under CC0; see `assets/audio/KENNEY_CC0_LICENSE.txt`
- Built with [Python](https://www.python.org/) and [Pygame](https://www.pygame.org/)

## Roadmap

- Controller support and remappable controls
- In-game tutorial cards for new mechanics
- Performance profiling and separation of the single-file prototype into modules
- Gameplay trailer, screenshots and a release page for downloadable builds

