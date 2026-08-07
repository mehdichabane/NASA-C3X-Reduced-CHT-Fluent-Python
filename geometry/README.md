# Geometry files

The geometry source is Hylton et al., NASA-CR-168015.

`raw/c3x_vane_profile_table3_xy_cm.csv` contains the external-vane
coordinates transcribed from Table III.

`raw/c3x_cooling_passages_figure7_uv_cm.csv` contains the ten cooling-passage
locations and diameters transcribed from Figure 7. It contains geometry only;
the internal-convection correction factors are stored separately under
`references/model_inputs/`.

The raw coordinates are retained in centimetres so they can be checked
directly against the NASA report.

`spaceclaim_imports/` contains the point-curve files used in SpaceClaim:

- vane profile;
- cooling-hole curves;
- one-pitch periodic passage boundary.

The SpaceClaim files use millimetres. Any length obtained by summing straight
segments between the tabulated points is a geometry-quality-control value, not
the exact arc length of the smoothed CAD curve.

The accepted meshes and the limits of the original interactive
meshing workflow are documented separately in
[`docs/meshing_recipe.md`](../docs/meshing_recipe.md). Missing GUI settings are
not inferred from the final topology.
