"""Create an explicit package mapping from the saved pre-migration inventory."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Outputs/Organization20261113'
baseline = json.loads((OUT / 'Baseline.json').read_text(encoding='utf-8'))
assert baseline.get('success')
mapping = {}
M = '/Game/Multimodal/'
main_text = json.dumps(baseline['maps']['/Game/TopDown/Lvl_TopDown']) + json.dumps(baseline['maps']['/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal'])
for row in baseline['assets']:
    old, cls = row['path'], row['class']
    name = old.rsplit('/', 1)[-1]
    new = None
    if old.startswith('/Game/Characters/Mannequins/'):
        new = old.replace('/Game/Characters/Mannequins/', '/Game/ExternalAssets/UnrealMannequins/', 1)
    elif old.startswith('/Game/LevelPrototyping/'):
        new = old.replace('/Game/LevelPrototyping/', '/Game/ExternalAssets/UnrealLevelPrototyping/', 1)
    elif old.startswith('/Game/CocoDetective/'):
        if cls == 'World':
            new = M + '90_Sandbox/Maps/CocoDetective/' + name.replace('Lvl_', 'LV_', 1)
        elif cls == 'Blueprint':
            role = 'Characters/Player' if name.endswith('Character') else 'Framework'
            new = M + '02_Blueprints/' + role + '/CocoDetective/' + name
        elif cls == 'MaterialInstanceConstant':
            new = M + '03_Graphics/Materials/Common/CocoDetective/' + name
        elif cls == 'StaticMesh':
            if any(word in name for word in ('Probe', 'ScaleGuide')) and name not in main_text:
                new = M + '90_Sandbox/Experiments/CocoDetective/Meshes/' + name
            elif name == 'SM_Coco':
                new = M + '03_Graphics/Meshes/Characters/Coco/' + name
            else:
                role = 'Buildings' if any(word in name for word in ('Alley', 'Gate', 'Office', 'Home', 'Walkway', 'Door', 'Wall', 'Floor', 'Window')) else 'Props'
                new = M + '03_Graphics/Meshes/' + role + '/CocoDetective/' + name
    elif old.startswith('/Game/TopDown/') or old.startswith('/Game/Cursor/'):
        subject = 'TopDown' if old.startswith('/Game/TopDown/') else 'Default'
        if cls == 'World':
            new = M + '01_Maps/Town/LV_CocoDetective_Town'
        elif cls == 'Blueprint':
            role = 'Characters/Player' if name.endswith('Character') else 'Framework'
            new = M + '02_Blueprints/' + role + '/TopDown/' + name
        elif cls in ('InputAction', 'InputMappingContext'):
            new = M + '07_Settings/Input/TopDown/' + name
        elif '/Cursor/' in old or old.startswith('/Game/Cursor/'):
            folders = {'NiagaraSystem': '08_Effects/Niagara', 'Material': '08_Effects/Materials', 'MaterialInstanceConstant': '08_Effects/Materials', 'Texture2D': '08_Effects/Textures', 'StaticMesh': '03_Graphics/Meshes/World'}
            new = M + folders[cls] + '/Cursor/' + subject + '/' + (name.replace('FX_', 'FXS_', 1) if cls == 'NiagaraSystem' else name)
        elif cls == 'MaterialInstanceConstant':
            new = M + '03_Graphics/Materials/Common/TopDown/' + name
    if old.startswith(('/Game/CocoDetective/', '/Game/TopDown/', '/Game/Cursor/', '/Game/Characters/', '/Game/LevelPrototyping/')):
        assert new, row
        mapping[old] = new
assert len(set(mapping.values())) == len(mapping), 'Destination collision'
existing = {row['path'] for row in baseline['assets']}
assert not (set(mapping.values()) & existing), 'Existing destination'
(OUT / 'AssetMoves.json').write_text(json.dumps(mapping, indent=2), encoding='utf-8')
print('Planned moves:', len(mapping))
