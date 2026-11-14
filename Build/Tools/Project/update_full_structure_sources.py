"""Update maintained text references and relocate vendor source artwork."""
import json
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[3]
out = root / 'Outputs/Organization20261113'
mapping = json.loads((out/'AssetMoves.json').read_text())
changed = []
paths = list((root/'Config').rglob('*.ini')) + list((root/'Build/Tools/ClientHome').rglob('*')) + list((root/'Docs/ClientHome').rglob('*.md')) + list((root/'SourceAssets').rglob('*.json'))
for path in paths:
    if not path.is_file() or path.suffix not in ('.ini','.py','.ps1','.dsl','.json','.md'): continue
    old = path.read_text(encoding='utf-8-sig')
    text = old
    for source,target in sorted(mapping.items(),key=lambda item:-len(item[0])):
        text = text.replace(source+'.'+source.rsplit('/',1)[-1], target+'.'+target.rsplit('/',1)[-1])
        text = text.replace(source,target)
    if path.name == 'DefaultEditorPerProjectUserSettings.ini':
        text = text.replace('/Game/TopDownBP','/Game/Multimodal')
    if old != text:
        path.write_text(text,encoding='utf-8')
        changed.append(str(path.relative_to(root)))
relocated = []
source_root = root/'Content/ExternalAssets/StylizedKitchen'
destination_root = root/'SourceAssets/ExternalAssets/StylizedKitchen'
for source in source_root.rglob('*'):
    if not source.is_file() or source.suffix.lower() not in ('.fbx','.tga'): continue
    target = destination_root/source.relative_to(source_root)
    if target.exists():
        if hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest():
            source.unlink()
            relocated.append({'source':str(source.relative_to(root)), 'target':str(target.relative_to(root)), 'identical_existing_copy':True})
            continue
        target = destination_root/'Imported'/source.relative_to(source_root)
        assert not target.exists(), target
    target.parent.mkdir(parents=True,exist_ok=True)
    source.rename(target)
    relocated.append({'source':str(source.relative_to(root)), 'target':str(target.relative_to(root))})
(out/'SourceChanges.json').write_text(json.dumps({'updated_text':changed,'source_art':relocated},indent=2),encoding='utf-8')
print('Updated text files:',len(changed),'Relocated source files:',len(relocated))
