# ClientHome clue change audit

- Rules: PROJECT_RULES.md; no new placement exceptions.
- Modified map: Content/Multimodal/01_Maps/ClientHome/LV_ClientHome_Linear.umap
- Modified GameMode: Content/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_GameMode_Linear.uasset
- New HUD actor Blueprint (not Widget Blueprint): Content/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_HUD_Linear.uasset
- New world highlight post-process material: Content/Multimodal/08_Effects/Materials/ClientHome/M_CH_ClueOutline.uasset
- Renderer configuration: Config/DefaultEngine.ini (r.CustomDepth=3).
- All new asset names use the required BP_ / M_ prefixes and existing ClientHome naming.
- 667 referenced game packages checked: no missing packages, Sandbox/Developers dependencies, or redirectors.
- HUD and GameMode Blueprint status: up to date. GameMode references the new Linear HUD.
- No dirty maps or content packages. git diff --check passed.
- Earlier runtime checks passed for collecting all five clues and disabling their outlines. Final location swap saved: fur between study desk and reading area; pawprints on bathroom entrance carpet.
- Outputs/ClientHomeLinear contains local automation scripts and inspection reports; keep outside the gameplay commit, consistent with preceding commits. No runtime asset dependency on these files.
- No commit or push performed during this audit. Packaged build not tested.
