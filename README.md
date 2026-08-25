# KI-Tools

A KiCad PCB editor plugin with a collection of small board-editing utilities
behind a simple UI of buttons and text boxes. All tool values are remembered
between sessions.

## Tools

### Font Fixer

Sets every text item on the selected layers to the same values in one go
(`fixfonts(x, y, z)`):

- **Font size** — text height in mm (`x`)
- **Line thickness** — text stroke width in mm (`y`)
- **Visible** — show or hide the text items (`z`, 0/1)
- **Layers** — top/bottom silkscreen and top/bottom fabrication

### Planned

- **Edge Line Equalizer** — make board edge line widths uniform
- **Fiducial Grid Placer** — place fiducials on a grid
- **Fix Vias** — via cleanup

## Installation

Via the KiCad Plugin and Content Manager (PCM) once published, or manually:
copy the package's `plugins/` folder contents into your KiCad scripting
plugins folder.

## Development status

Initial scaffold (0.1.0). Tool logic is being ported from existing scripts.

## License

GPL-3.0 — see LICENSE.
