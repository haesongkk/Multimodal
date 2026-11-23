# ClientHome Storybook comparison

Maintained usage and layout documentation: `Docs/ClientHome/StyleComparison.md`.
This file records the art-generation and validation work for the comparison.

F1 Original, F2 Storybook. F6/F7 retain camera presets.
Papercraft and Kenney comparison maps were removed; shared props required by Storybook remain.
Changing the comparison reloads its map and resets investigation progress.

Storybook preserves the existing furniture footprints and clue anchors. It combines
new beveled furniture with selected original curved fixtures and authored support props.
Walnut, sage, ivory, ochre upholstery, paneled walls, subtle wood grain, woven rugs,
and four illustrated paintings provide a consistent warm storybook direction.
The player character is unchanged; the supplied detective image is an art reference.

Sources: SourceAssets/ClientHome/Storybook/build_models.py and its FBX outputs.
Map: /Game/Multimodal/90_Sandbox/Maps/ClientHome/LV_ClientHome_Storybook
Build: build_storybook.py followed by polish_storybook.py (readable clock faces).
The generated art atlas is SourceAssets/ClientHome/Storybook/T_CH_StorybookArt.png.
It was made with the built-in image-generation tool: four equal quadrants, warm
gouache/cut-paper illustrations of an orange cat at a window, a forest cottage,
yellow flowers in a vase, and a lake at sunset; cream, sage, dusty blue and ochre.
This is a description of the generation brief, not a verbatim prompt archive.

Validation: five clues passed proximity, collection count and highlight-removal checks.
F1 and F2 were pressed after cleanup and opened Original and Storybook respectively.
The dependency audit checked 726 packages: no missing references, redirectors or
unsaved packages. The original tracked production assets have no diff.
Packaged-build testing and replacement of the player character were not performed.
No commit or push performed for these comparison maps.
