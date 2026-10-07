# rdla_wedge

A tool to create a wedge of variations from an otherwise static RDLA scene. It is useful for things like:
* Sweeping one attribute to understand how it behaves across a range of values
* Generating a small GIF to demonstrate a feature or the impact of adjusting some setting
* Creating a simple "spin" animation to showcase a model or material

> For the full, up-to-date flag reference and a set of runnable usage examples, run `rdla_wedge --help`. This README only covers concepts and mechanics that don't fit well in `--help` output.

## Description

This script takes MoonRay scene file(s) (.rdla/.rdlb), renders multiple frames with varying `wedge` and `frame_num` variables, and outputs the result as an animated GIF, MP4 video, or image sequence.

The tool has two modes:
1. **Manual Mode** (default): Injects `wedge` and `frame_num` variables for you to reference directly in your rdla files, to drive any attribute (or any behavior at all, since RDLA is Lua) however you like
2. **Automatic Mode**: Additionally animates one or more attributes, across one or more SceneObjects (materials, maps, lights, cameras, geometry, etc.) or SceneVariables, by creating a sidecar rdla file that overrides them with a formula based on the `wedge` variable

## Usage

```
rdla_wedge [options] <rdla/rdlb file> [rdla/rdlb file2] [...] <frames> <output1> [output2] [...]
```

### Required Arguments

- `<rdla/rdlb file> [rdla/rdlb file2] [...]` - Path(s) to MoonRay scene file(s). Multiple rdla/rdlb files can be specified. Later files override/extend earlier ones.
- `<frames>` - Number of frames to render
- `<output1> [output2] ...` - One or more output files (gif/mp4) or patterns (image sequence)

### Output Formats

- **GIF**: `output.gif`
- **MP4**: `output.mp4`
- **Image Sequence**: `out.*.exr`, `frames.*.jpg`, etc. (the `*` is replaced with frame numbers)
- **Multiple Outputs**: Specify multiple outputs to generate different formats simultaneously

## Manual Mode

The tool always injects two variables into your scene via `-rdla_set`, regardless of mode:
- `wedge`: Animates from [0,1) by default, or [0,1] with `--inclusive`
- `frame_num`: The current frame number (0-based)

In manual mode specifically (i.e. without `--wedge-attribute`), these injected variables are the *only* thing driving the render - you must reference them directly in your rdla file(s) or create your own sidecar file that references them to drive any attribute you want to wedge.
No sidecar file is created automatically for you; your input files are used directly.

Example sidecar rdla file that uses the `wedge` variable:

```lua
-- sidecar.rdla
EnvLight("myLight") {
    ["node_xform"] = rotate(360 * wedge, 0, 1, 0)  -- full rotation over wedge range
}

Material("myMaterial") {
    ["roughness"] = 0.1 + (0.9 * wedge)  -- roughness from 0.1 to 1.0
}
```

## Automatic Mode

Use `--wedge-attribute <object-name|sv> <attr> <min> <max>` to have the tool automatically animate a specific attribute instead of writing the Lua formula yourself. The tool will:
- Create a sidecar rdla file containing only the animated attribute override(s), expressed as a Lua formula using `wedge` (e.g. `["roughness"] = (0 + wedge * 1)`) - since the sidecar is loaded last and merges into the already-loaded SceneObject/SceneVariables (rather than replacing it), any attribute not mentioned simply keeps the value it already has
- Append the sidecar file automatically during rendering, so it overrides the input file(s) without ever modifying them

`--wedge-attribute` may be repeated to animate several attributes, across several different objects, together in the same wedge - every repetition is driven by the same underlying `wedge` value (optionally reshaped via `--power`/`--pingpong`, which apply globally to all animated attributes).

Use `sv` as the object name to animate a SceneVariables attribute instead of a SceneObject's.

### Multi-Object Label Prefixing

This applies to `--wedge-attribute` (automatic mode) and `--overlay-static-attributes` (which works in either mode) together: when more than one distinct object is involved overall (counting both `--wedge-attribute` targets and any `--overlay-static-attributes` targets),
text labels from `--overlay-wedged-attributes` and `--overlay-static-attributes` are automatically prefixed with the object name (e.g. `GlassLeft.refractive_index`, `GlassRight.refractive_index`) to disambiguate them. With only a single object involved, labels are shown unprefixed (e.g. `roughness`).

## Choosing Between Modes

Automatic mode is the easier choice for the common case: linear (or ping-pong) interpolation of one or more attributes between a min and max value. It also comes with the text overlay "for free" - `--overlay-wedged-attributes` automatically shows the animated attribute's name and current value on each frame,
with no need to write your own `--overlay-expr` formula just to display it.

Manual mode is the better choice whenever you need logic beyond "interpolate between two values," since RDLA is Lua and the injected `wedge`/`frame_num` variables can drive anything Lua can express. For example:

- **Non-linear curves**: `["roughness"] = 0.1 + 0.9 * (wedge * wedge)` (ease-in quadratic, or any custom formula)
- **Conditionals**: switch between two completely different attribute values, or even swap which SceneObject is bound somewhere, partway through the wedge (e.g. `if wedge > 0.5 then ... end`)
- **Loops**: procedurally generate a list of attribute overrides or a `SceneObjectVector`/light list whose size or contents depend on `frame_num`
- **Driving multiple interdependent attributes from one shared expression**, including attributes `--wedge-attribute` can't target at all (e.g. structural/list-valued attributes, bindings, geometry sets)
- **Randomization** seeded deterministically by `frame_num`, for noise/variation across frames

In manual mode, any text overlay beyond the built-ins (`--wedge-label`, `--overlay-mcrt`, `--overlay-frame`) has to be written yourself via `--overlay-expr`.

## Notes

- The tool creates temporary files in `/tmp/rdla_wedge/`
- Your original rdla/rdlb files are never modified
- Multiple rdla/rdlb files can be specified - later files override/extend earlier ones
- Image sequences with `.exr` extension are copied directly; other formats are converted
- By default, animations are linear (min→max); use `--pingpong` for back-and-forth (min→max→min)

See `rdla_wedge --help` for the complete, authoritative list of options and runnable examples covering text overlays (`--overlay-wedged-attributes`, `--overlay-static-attributes`, `--overlay-expr`, `--overlay-mcrt`, `--overlay-frame`), rendering/workflow options, and more.
