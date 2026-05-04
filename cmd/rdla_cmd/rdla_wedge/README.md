# rdla_wedge

A tool to create animated wedges of MoonRay renders. By default, it injects a `wedge` variable (0-1) that you can use in your rdla files to drive any parameter. Optionally, it can also automatically animate a specific parameter on a material, map, or SceneVariables.

## Description

This script takes MoonRay scene file(s) (.rdla/.rdlb), renders multiple frames with varying `wedge` and `frame_num` variables, and outputs the result as an animated GIF, MP4 video, or image sequence.

The tool has two modes:
1. **Generic Wedge Mode** (default): Injects `wedge` and `frame_num` variables for you to use in your rdla files
2. **Parameter Animation Mode**: Additionally animates a specific parameter by creating a sidecar rdla file

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

## Examples

### Basic Generic Wedge Mode (Default)

In generic wedge mode, the tool injects two variables into your scene:
- `wedge`: Animates from [0,1) by default, or [0,1] with `--inclusive`
- `frame_num`: The current frame number (0-based)

You reference these variables in your rdla files to drive any parameter you want.

```bash
# Inject wedge variable from [0,1) over 180 frames
rdla_wedge scene.rdla 180 output.mp4

# Make wedge range [0,1] (includes 1.0 on last frame)
rdla_wedge --inclusive scene.rdla 180 output.mp4

# Add text overlay showing wedge value
rdla_wedge --wedge-label "rotation" scene.rdla 180 output.mp4

# Apply power curve to wedge interpolation
rdla_wedge --power 2.0 scene.rdla 100 output.gif
```

Example rdla file using the `wedge` variable:

```lua
-- spin.rdla
EnvLight("myLight") {
    ["node_xform"] = rotate(360 * wedge, 0, 1, 0)  -- full rotation over wedge range
}

Material("myMaterial") {
    ["roughness"] = 0.1 + (0.9 * wedge)  -- roughness from 0.1 to 1.0
}
```

### Parameter Animation Mode

Use the `--animate-parameter` option to automatically animate a specific parameter. The tool will:
- Create a sidecar rdla file with the animated parameter
- Still inject `wedge` and `frame_num` variables
- Apply the interpolated parameter value through the generated sidecar rdla file

```bash
# Animate roughness from 0 to 1 over 20 frames
rdla_wedge --animate-parameter "MyMaterial roughness 0 1" scene.rdla 20 output.gif

# Animate specular color from red to blue over 30 frames
rdla_wedge --animate-parameter "MyMaterial specular 1,0,0 0,0,1" scene.rdla 30 output.mp4

# Animate SceneVariables pixel samples from 1 to 16 over 10 frames
rdla_wedge --animate-parameter "sv pixel_samples 1 16" scene.rdla 10 output.mp4

# Add text overlay showing the parameter value
rdla_wedge --animate-parameter "MyMaterial roughness 0 1" scene.rdla 20 output.mp4 \
  --overlay-parameter
```

**Parameter Format**: `--animate-parameter "<object_name> <param_name> <min_value> <max_value>"`
- For `sv` (SceneVariables): `--animate-parameter "sv <param_name> <min> <max>"`
- For materials/maps: `--animate-parameter "<object_name> <param_name> <min> <max>"`
- Multi-component values: Use commas (e.g., `1,0,0` for RGB)

**Note**: In parameter animation mode, the tool creates a sidecar rdla file that includes all parameters from the material/map/sv along with the animated parameter override. Your original files are never modified.

### Multiple RDLA/RDLB Files

You can specify multiple rdla/rdlb files to layer scenes. Later files override/extend parameters from earlier files. This is useful for separating base scene setups from material/lighting overrides.

```bash
# Generic wedge mode with multiple files
rdla_wedge base_scene.rdla material_overrides.rdla 20 output.mp4

# Parameter animation with multiple files
rdla_wedge --animate-parameter "MyMaterial roughness 0 1" \
  base_scene.rdla material_overrides.rdla 20 output.mp4

# Mix rdlb and rdla files
rdla_wedge base.rdlb lighting.rdlb material_tweaks.rdla \
  180 output.mp4
```

### Image Sequence Output

```bash
# Export as JPEG sequence (generic wedge mode)
rdla_wedge scene.rdla 10 frames/out.*.jpg

# Export as EXR sequence (no conversion, just copies)
rdla_wedge scene.rdla 10 renders/out.*.exr

# With parameter animation
rdla_wedge --animate-parameter "MyMaterial roughness 0 1" scene.rdla 10 frames/out.*.jpg
```

### Multiple Outputs

```bash
# Generate both MP4 and image sequence
rdla_wedge scene.rdla 5 \
  ./output/frames.*.jpg \
  ./output/animation.mp4

# With parameter animation
rdla_wedge --animate-parameter "sv bsdf_samples 1 5" scene.rdla 5 \
  ./output/frames.*.jpg \
  ./output/animation.mp4
```

### With Text Overlay

```bash
# Show wedge value in generic wedge mode
rdla_wedge --wedge-label "rotation" scene.rdla 20 output.mp4

# Show parameter value in parameter animation mode
rdla_wedge --animate-parameter "MyMaterial roughness 0 1" scene.rdla 20 output.mp4 \
  --overlay-parameter

# Show MCRT render time
rdla_wedge scene.rdla 20 output.mp4 --overlay-mcrt

# Show frame number
rdla_wedge scene.rdla 20 output.mp4 --overlay-frame

# Position text at the top instead of bottom
rdla_wedge scene.rdla 20 output.mp4 \
  --wedge-label "rotation" \
  --textposition top

# Customize text appearance
rdla_wedge scene.rdla 20 output.mp4 \
  --wedge-label "rotation" \
  --textcolor red \
  --textsize 30
```

### Linear Animation (No Ping-Pong)

```bash
# By default, animation is linear (min->max)
# Use --pingpong for back-and-forth animation (min->max->min)
rdla_wedge --animate-parameter "MyMaterial roughness 0 1" scene.rdla 10 output.gif --pingpong

# Also works in generic wedge mode (no --animate-parameter)
rdla_wedge scene.rdla 10 output.gif --pingpong
```

## Common Options

### Mode Selection
- `--animate-parameter "<object> <param> <min> <max>"` - Enable parameter animation mode (animates a specific parameter)

### Text Overlay Options
- `--wedge-label <label>` - Show wedge value with custom label (generic wedge mode)
- `--overlay-parameter` - Overlay the parameter value as text on each frame (parameter animation mode)
- `--overlay-mcrt` - Overlay the MCRT render time on images
- `--overlay-frame` - Overlay the frame number on images
- `--textposition <top|bottom>` - Position of text overlay (default: bottom)
- `--textsize <size>` - Point size of text (default: 20)
- `--textcolor <color>` - Color of text overlay (default: white)
- `--overlay-additional-parameters <params>` - Comma-separated list of additional parameters to show as text (parameter animation mode)

### Animation Options
- `--power <value>` - Power for interpolation curve (default: 1.0 for linear)
- `--pingpong` - Pingpong the animation (min→max→min) instead of linear (min→max)
- `--inclusive` - Make wedge range [0,1] instead of [0,1) (includes 1.0 on last frame)

### Rendering Options
- `--exec_mode <mode>` - Moonray execution mode: scalar, vector, xpu, or auto (default: auto)
- `--max-concurrent-jobs <n>` - Maximum number of parallel rendering/conversion processes (default: 16)
- `--no-clean` - Don't clean the temp directory before starting (default is to clean)
- `-v, --verbose` - Verbose output with timing information

### Workflow Options
- `--skiprender` - Don't render, only convert to gif/mp4 (assumes images are present)

## Variables Injected

The tool always injects these variables into your scene via `-rdla_set`:
- `wedge` - Float value from [0,1) or [0,1] (with --inclusive)
- `frame_num` - Integer frame number (0-based)

In parameter animation mode (with `--animate-parameter`), the sidecar rdla file also contains the animated parameter value, expressed as a Lua formula using the `wedge` variable (e.g., `["roughness"] = (0 + wedge * 1)`).

## Notes

- The tool creates temporary files in `/tmp/rdla_wedge/`
- Your original rdla/rdlb files are never modified
- Multiple rdla/rdlb files can be specified - later files override/extend earlier ones

**Parameter Animation Mode:**
- A sidecar rdla file is created containing all material/map parameters plus the animated parameter
- The sidecar file is added last during rendering to override the input files
- Your original input files are never modified
- Use `sv` as the material/map name to animate SceneVariables parameters
- Frame interpolation uses the `wedge` variable in Lua expressions (e.g. `["roughness"] = (0 + wedge * 1)`)

**Generic Wedge Mode (default when no parameter is specified):**
- Injects global `wedge` (0-1) and `frame_num` variables via `-rdla_set`
- No sidecar file is created - original files are used directly
- Wedge range is [0,1) by default, or [0,1] with `--inclusive`
- Reference `wedge` and `frame_num` variables in your rdla files

**General:**
- By default, animations are linear (min→max); use `--pingpong` for back-and-forth (min→max→min)
- Image sequences with `.exr` extension are copied directly; other formats are converted
- Multiple outputs can be specified to generate different formats in one render pass
- Power curves can be applied to interpolation with `--power`

## Examples with All Features

```bash
# Full example: SceneVariables animation with text overlay and multiple outputs
rdla_wedge --animate-parameter "sv bsdf_samples 1 16" \
  scene.rdla 10 \
  --overlay-parameter \
  --textposition top \
  --textcolor cyan \
  --textsize 24 \
  --verbose \
  ./renders/bsdf_samples.*.exr \
  ./renders/bsdf_samples.mp4 \
  ./renders/bsdf_samples.gif
```
