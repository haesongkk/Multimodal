import bpy
from pathlib import Path
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Detective_Structured_Working.blend'))
o=bpy.data.objects['02_Coat_Shoulder_Sleeve_Hip_Loops']
for z in [-.35,-.32,-.285,-.25,-.37,-.395]:
    print(z,[(round(v.co.x,4),round(v.co.y,4),round(v.co.z,4)) for v in o.data.vertices if abs(v.co.z-z)<.00001 and abs(v.co.x)<.25 and v.co.y<-.1])
print('BOTTOMFACES',[(p.index, [tuple(round(x,3) for x in o.data.vertices[i].co) for i in p.vertices]) for p in o.data.polygons if p.center.z<-.28 and p.center.z>-.36 and p.normal.z<-.9][:10])
