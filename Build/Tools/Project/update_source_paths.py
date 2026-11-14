"""One-time companion migration of text sources; never moves Unreal packages."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[3]
mapping = json.loads((root/'Outputs/Organization/AssetMoves.json').read_text())
prefixes = [
    ('/UI/Cozy/F_Jua', '/04_UI/Fonts/ClientHome/FNT_Jua'),
    ('/UI/Cozy/Jua.Jua', '/04_UI/Fonts/ClientHome/FF_Jua.FF_Jua'),
    ('/UI/Cozy', '/04_UI/Textures/ClientHome'),
    ('/UI/WBP_', '/04_UI/Widgets/ClientHome/WBP_'),
    ('/Blueprints/BP_CH_Player', '/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player'),
    ('/Blueprints/BP_CH_Door', '/02_Blueprints/Buildings/ClientHome/BP_CH_Door'),
    ('/Blueprints/', '/02_Blueprints/Framework/ClientHome/'),
    ('/Maps/Lvl_ClientHome_Blockout', '/90_Sandbox/Maps/ClientHome/LV_ClientHome_Blockout'),
    ('/Maps/Lvl_ClientHome_Minimal', '/01_Maps/ClientHome/LV_ClientHome_Minimal'),
    ('/Materials/', '/03_Graphics/Materials/Buildings/ClientHome/'),
    ('/Meshes/', '/03_Graphics/Meshes/Buildings/ClientHome/'),
]
files = list((root/'Build/Tools/ClientHome').glob('*')) + list((root/'Docs/ClientHome').glob('*.md')) + list((root/'SourceAssets/ClientHome/UIArt').glob('*.md')) + list((root/'SourceAssets/Data/ClientHome').glob('*.json'))
for path in files:
    if not path.is_file() or path.suffix not in ('.py','.dsl','.ps1','.md','.json'): continue
    text = path.read_text(encoding='utf-8-sig')
    # Complete references, including object names, before variable-based paths.
    for old,new in sorted(mapping.items(),key=lambda x:-len(x[0])):
        text=text.replace(old+'.'+old.rsplit('/',1)[-1],new+'.'+new.rsplit('/',1)[-1]).replace(old,new)
    # Only relative literals on ROOT/root; do not rewrite provider paths.
    for old,new in prefixes:
        for quote in ("'", '"'):
            text=text.replace(quote+old,quote+new)
        text=text.replace('Content/ClientHome_Haeso'+old,'Content/Multimodal'+new)
    text=text.replace('/Game/ClientHome_Haeso','/Game/Multimodal')
    text=text.replace('/Game/StylizedKitchen','/Game/ExternalAssets/StylizedKitchen')
    text=text.replace('Development/ClientHome','Build/Tools/ClientHome')
    text=text.replace('D:/Multimodal/Saved/ClientHome','D:/Multimodal/Outputs/ClientHome')
    text=text.replace('Lvl_ClientHome_Minimal.Lvl_ClientHome_Minimal','LV_ClientHome_Minimal.LV_ClientHome_Minimal')
    text=text.replace("ART=OUT/'UIArt'", "ART=OUT.parents[2]/'SourceAssets/ClientHome/UIArt'")
    if path.name=='Launch-ClientHomeEditor.ps1':text=text.replace("'../..'","'../../..'")
    if path.name=='build_small_bathroom.py':text=text.replace("(base/'example-furnishings.json')", "(Path('D:/Multimodal/SourceAssets/Data/ClientHome/example-furnishings.json'))")
    if path.name=='inspect_example_furniture.py':text=text.replace('Outputs/ClientHome/example-furnishings.json','SourceAssets/Data/ClientHome/example-furnishings.json')
    path.write_text(text,encoding='utf-8')
ignore=root/'.gitignore'
text=ignore.read_text().replace('/Content/StylizedKitchen/','/Content/StylizedKitchen/\n/Content/ExternalAssets/StylizedKitchen/')
text+='\n# Versioned editor/build support tools.\n!Build/Tools/\n!Build/Tools/**\n'
ignore.write_text(text)
