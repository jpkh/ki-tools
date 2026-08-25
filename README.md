# KI-Tools

A KiCad PCB editor plugin with a collection of small board-editing utilities
behind a simple UI of buttons and text boxes. All tool values are remembered
between sessions.

## Tools

### Text Size Fixer

Sets footprint reference and value texts on the selected layers to the same
size, thickness and visibility in one go:

- **Text size** — text height in mm
- **Thickness** — text stroke width in mm
- **Visible** — show or hide the text items
- **Layers** — top/bottom silkscreen (`F.SilkS`, `B.SilkS`) and top/bottom
  fabrication (`F.Fab`, `B.Fab`)

Texts on fiducial / mounting-hole / tooling footprints, references like
`G201` or `FIDORIG1` and values like `LOGO` are hidden automatically.

### Fix Vias

Resizes every via matching a given old diameter and drill to a new diameter
and drill.

### Planned

- **Edge Line Equalizer** — make board edge line widths uniform
- **Fiducial Grid Placer** — place fiducials on a grid

## Installation

Via the KiCad Plugin and Content Manager (PCM) once published, or manually:
copy the package's `plugins/` folder contents into your KiCad scripting
plugins folder.

## Development status

Initial scaffold (0.1.0). Tool logic is being ported from existing scripts.

## License

GPL-3.0 — see LICENSE.
