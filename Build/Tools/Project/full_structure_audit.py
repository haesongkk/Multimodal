"""Capture maps and package inventory before/after a whole-project reorganization."""
import unreal as u
import json
import traceback
from pathlib import Path

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Outputs/Organization20261113'
OUT.mkdir(parents=True, exist_ok=True)

def snapshot():
    rows = []
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        data = {'name': actor.get_name(), 'label': actor.get_actor_label(), 'class': actor.get_class().get_path_name(), 'transform': str(actor.get_actor_transform()), 'components': []}
        for component in actor.get_components_by_class(u.MeshComponent):
            entry = {'name': component.get_name(), 'materials': [m.get_path_name() if m else None for m in component.get_materials()]}
            if isinstance(component, u.StaticMeshComponent):
                mesh = component.get_editor_property('static_mesh')
                entry['mesh'] = mesh.get_path_name() if mesh else None
            elif isinstance(component, u.SkeletalMeshComponent):
                mesh = component.get_editor_property('skeletal_mesh_asset')
                entry['mesh'] = mesh.get_path_name() if mesh else None
                anim = component.get_editor_property('anim_class')
                entry['animation'] = anim.get_path_name() if anim else None
            data['components'].append(entry)
        data['components'].sort(key=lambda item: item['name'])
        rows.append(data)
    return sorted(rows, key=lambda item: item['name'])

def run():
    report = {'assets': [], 'maps': {}}
    try:
        registry = u.AssetRegistryHelpers.get_asset_registry()
        registry.search_all_assets(True)
        for data in registry.get_assets_by_path('/Game', recursive=True):
            report['assets'].append({'path': str(data.package_name), 'class': str(data.asset_class_path.asset_name)})
        levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
        maps = sorted(row['path'] for row in report['assets'] if row['class'] == 'World')
        for package in maps:
            assert levels.load_level(package), package
            report['maps'][package] = snapshot()
            (OUT / 'Baseline.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        report['success'] = True
    except Exception:
        report['success'] = False
        report['error'] = traceback.format_exc()
    (OUT / 'Baseline.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    run()
