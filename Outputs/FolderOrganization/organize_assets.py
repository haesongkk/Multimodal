"""Read-only local planner. Does not import Unreal or move/save assets."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'Outputs' / 'FolderOrganization'
before = json.loads((out / 'inventory_before.json').read_text(encoding='utf-8'))

def target(asset):
    path, cls = asset['path'], asset['class']
    name = path.rsplit('/', 1)[-1]
    own = '/Game/Multimodal/'
    if path == '/Game/TopDown/Lvl_TopDown':
        return own + '01_Maps/TopDown/LV_TopDown'
    if path.startswith('/Game/CocoDetective/Backups/'):
        return own + '90_Sandbox/Maps/Backups/' + name.replace('Lvl_', 'LV_', 1)
    if path.startswith('/Game/CocoDetective/Maps/'):
        return own + '01_Maps/Alley/' + name.replace('Lvl_', 'LV_', 1)
    if path.startswith('/Game/CocoDetective/Fab/'):
        return path.replace('/Game/CocoDetective/Fab/', '/Game/ExternalAssets/', 1)
    for folder in ['Characters', 'LevelPrototyping', 'Cursor', 'TopDown']:
        prefix = '/Game/' + folder + '/'
        if path.startswith(prefix):
            return path.replace('/Game/', '/Game/ExternalAssets/UnrealTemplates/', 1)
    if path.startswith('/Game/CocoDetective/Blueprints/'):
        folder = 'Characters/Player/' if name.endswith('Character') else 'Framework/'
        return own + '02_Blueprints/' + folder + name
    if path.startswith('/Game/CocoDetective/Input/'):
        return own + '07_Settings/Input/' + name
    if path.startswith('/Game/CocoDetective/Materials/'):
        return own + '03_Graphics/Materials/CocoDetective/' + name
    if path.startswith('/Game/CocoDetective/Props/Meshes/'):
        return own + '03_Graphics/Meshes/Props/' + name
    if path.startswith('/Game/CocoDetective/Meshes/'):
        if any(word in name for word in ['Probe', 'ScaleGuide']):
            return own + '90_Sandbox/Experiments/Meshes/' + name
        return own + '03_Graphics/Meshes/CocoDetective/' + name
    if path.startswith('/Game/CocoDetective/Characters/Detective/'):
        folder = {'Texture2D':'Textures', 'Material':'Materials', 'SkeletalMesh':'Meshes'}.get(cls, 'Animations')
        return own + '03_Graphics/' + folder + '/Characters/Detective/' + name
    return path

plan = [dict(asset, destination=target(asset)) for asset in before['assets'] if target(asset) != asset['path']]
destinations = [row['destination'] for row in plan]
assert len(set(destinations)) == len(destinations), 'Duplicate destination'
(out / 'move_manifest.json').write_text(json.dumps(plan, indent=2), encoding='utf-8')

print(json.dumps({'planned_assets':len(plan), 'maps':[row for row in plan if row['class']=='World']}, indent=2))
