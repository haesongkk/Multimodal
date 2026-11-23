import unreal as u,json,math
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=u.load_asset('/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Linear');g=B.get_graph(bp,'ApplyCameraPreviewFrame');types=json.loads((_linear_root/'camera_frame_types.json').read_text());m=json.loads((_linear_root/'frame_math_types.json').read_text())
def node(t,x,y=0):return B.create_node(g,t,u.IntPoint(x,y))
def link(a,b):assert a.try_create_connection(b)
def mapnode(source,ia,ib,oa,ob,x,y=200):
 n=node(types['MapRangeClamped'][0],x,y);link(source,n.find_input_pin('Value'))
 for p,v in [('InRangeA',ia),('InRangeB',ib),('OutRangeA',oa),('OutRangeB',ob)]:n.find_input_pin(p).set_pin_value(str(float(v)))
 return n
entry=B.find_nodes(g,node_class=u.K2Node_FunctionEntry.static_class())[0]
for old in B.find_nodes(g):
 if old!=entry:B.delete_node(old)
a=node(types['GetCameraPreviewAngle'][0],0,200)
height=mapnode(a.find_result_pin(),15,25,350,480,200)
sh=node(types['SetCameraPreviewHeight'][0],450);link(entry.find_then_pin(),sh.find_execute_pin());link(height.find_result_pin(),sh.find_input_pin('CameraPreviewHeight'))
num=mapnode(sh.find_output_pin('Output_Get'),0,1000,20,-980,650)
vhalf=math.degrees(math.atan(math.tan(math.radians(30))/(16/9)))
angle=mapnode(a.find_result_pin(),15,35,15+vhalf,35+vhalf,650,400)
tan=node(next(t for t in m['tan(degrees)'] if t.endswith('|Tan(Degrees)')),850,400);link(angle.find_result_pin(),tan.find_data_input_pin())
div=node(m['SafeDivide'][0],1050,200);link(num.find_result_pin(),div.find_input_pin('A'));link(tan.find_result_pin(),div.find_input_pin('B'))
sd=node(types['SetCameraPreviewDepth'][0],1250);link(sh.find_then_pin(),sd.find_execute_pin());link(div.find_result_pin(),sd.find_input_pin('CameraPreviewDepth'))
B.compile_blueprint(bp)
# Existing horizontal follow stays intact; replace only camera depth/height inputs.
eg=B.get_graph(bp,'EventGraph');wired=0
for n in B.find_nodes(eg):
 z=n.find_input_pin('Z');y=n.find_input_pin('Y')
 if z.is_valid() and y.is_valid() and z.get_pin_value() in ['520.0','520.000000']:
  gh=B.create_node(eg,types['GetCameraPreviewHeight'][0],u.IntPoint(0,3800));gd=B.create_node(eg,types['GetCameraPreviewDepth'][0],u.IntPoint(0,4000))
  z.break_pin_links();y.break_pin_links();link(gh.find_result_pin(),z);link(gd.find_result_pin(),y);wired+=1
step=B.get_graph(bp,'StepCameraPreviewAngle');pr=next(n for n in B.find_nodes(step) if 'PrintString' in str(n.get_node_title()).replace(' ',''))
call=B.create_node(step,B.find_node_types(step,'ApplyCameraPreviewFrame')[0],u.IntPoint(1850,0));link(pr.find_then_pin(),call.find_execute_pin())
B.compile_blueprint(bp);cdo=u.get_default_object(bp.generated_class());cdo.set_editor_property('CameraPreviewHeight',480.);cdo.set_editor_property('CameraPreviewDepth',(20-480)/math.tan(math.radians(25+vhalf)))
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(bp)
(_linear_root/'camera_auto_frame_result.json').write_text(json.dumps({'camera_vectors_wired':wired,'vertical_half_fov':vhalf,'status':str(bp.get_editor_property('status'))},indent=2))
