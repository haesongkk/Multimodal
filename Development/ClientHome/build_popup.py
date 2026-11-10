"""Build the owned UMG popup. Run before build_gameplay.py, with PIE stopped."""
import json
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as B
from editor_toolset.toolsets.object import ObjectTools as O

ROOT = '/Game/ClientHome_Haeso'
OUT = Path(__file__).resolve().parent

def build_popup():
    assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop PIE first'
    dirty = list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    assert all(p.get_name().startswith(ROOT + '/') for p in dirty), 'Foreign unsaved packages'
    path = ROOT + '/UI/WBP_CH_Popup'
    if assets.does_asset_exist(path):
        bp = assets.load_asset(path)
    else:
        factory = u.WidgetBlueprintFactory()
        factory.set_editor_property('parent_class', u.UserWidget)
        bp = u.AssetToolsHelpers.get_asset_tools().create_asset('WBP_CH_Popup', ROOT+'/UI', u.WidgetBlueprint, factory)
    tool = u.get_default_object(u.UMGToolSet)
    items = {str(i.widget_name):i for i in tool.call_method('GetWidgets', (bp,)).widgets}
    def add(name, cls, parent=None):
        info = items.get(name) or tool.call_method('AddWidget', (bp, cls.static_class(), name, parent, -1))
        items[name] = info
        return info.widget
    def read(obj, names):
        schema = json.loads(O.list_properties(obj))
        assert set(names) <= set(schema), (names, list(schema))
        return json.loads(O.get_properties(obj, names))
    def write(obj, values):
        read(obj, list(values))
        assert O.set_properties(obj, json.dumps(values, ensure_ascii=False))
    def margin(l,t,r,b): return dict(left=l,top=t,right=r,bottom=b)
    root = add('PopupRoot', u.CanvasPanel)
    card = add('PopupCard', u.Border, root)
    content = add('PopupContent', u.VerticalBox, card)
    # Bottom anchored, horizontally stretched card. Auto height follows wrapped text.
    write(items['PopupCard'].slot, {'layoutData':{
        'anchors':{'minimum':{'x':.08,'y':.94},'maximum':{'x':.92,'y':.94}},
        'offsets':margin(0,0,0,0),'alignment':{'x':0,'y':1}}, 'bAutoSize':True})
    brush = read(card,['background'])['background']
    brush.update(drawAs='RoundedBox')
    brush['outlineSettings'].update(cornerRadii=dict(x=12,y=12,z=12,w=12),roundingType='FixedRadius')
    write(card, {'background':brush,'brushColor':dict(r=.025,g=.04,b=.045,a=.97),'padding':margin(28,22,28,20)})
    write(items['PopupContent'].slot, {'padding':margin(28,22,28,20)})
    for name,size,color,weight,pad in [
        ('PopupTitle',28,(1,.69,.29),'Bold',margin(0,0,0,12)),
        ('PopupMessage',22,(.94,.95,.91),'Regular',margin(0,0,0,18)),
        ('PopupHint',16,(.65,.78,.75),'Regular',margin(0,0,0,0))]:
        widget=add(name,u.TextBlock,content)
        tool.call_method('ToggleWidgetAsVariable',(bp,widget,True))
        font=read(widget,['font'])['font']; font.update(size=size,typefaceFontName=weight)
        write(widget,{'font':font,'autoWrapText':True,'wrappingPolicy':'AllowPerCharacterWrapping',
            'colorAndOpacity':{'specifiedColor':dict(zip(('r','g','b','a'),(*color,1))),'colorUseRule':'UseColor_Specified'},
            'text':{'PopupTitle':'의뢰인 집','PopupMessage':'코코가 집 밖으로 나간 경로를 찾아보자.','PopupHint':'[Enter] 확인'}[name]})
        write(items[name].slot,{'padding':pad})
    write(root,{'visibility':'HitTestInvisible'})
    assert tool.call_method('CompileWidgetBlueprint',(bp,))
    graph=B.add_function_graph(bp,'Present')
    for name,typ in [('Heading','text'),('Body','text'),('Shown','bool'),('Finished','bool')]:
        if not B._param_name_exists(graph,name,True): B.add_function_param(graph,name,typ,True)
    B.compile_blueprint(bp)
    def node(term, prefix=None):
        ids=sorted(set(i for i in B.find_node_types(graph,term) if i.split('|')[-1]==term and (not prefix or i.startswith(prefix))))
        assert len(ids)==1,(term,ids)
        B.get_node_type_pins(graph,ids[0])
        return ids[0]
    text=node('SetText(Text)')
    visibility=next(i for i in B.find_node_types(graph,'SetVisibility') if i.split('|')[-1]=='SetVisibility' and any(p.name=='InVisibility' for p in B.get_node_type_pins(graph,i).input_pins))
    statements=[]
    for name,value in [('PopupTitle','Heading'),('PopupMessage','Body'),('PopupHint','(select Finished "[Esc] 테스트 종료" "[Enter] 확인  ·  읽는 동안 이동이 멈춥니다")')]:
        statements.append(f'({text} :self ({node("Get"+name,"Variables|")}) :InText {value})')
    code='(fn Present (Heading Body Shown Finished)\n'+'\n'.join(statements)+f'\n(if Shown ({visibility} :self self :InVisibility "HitTestInvisible") (else ({visibility} :self self :InVisibility "Collapsed"))))'
    B.write_graph_dsl(graph,code)
    (OUT/'WBP_CH_Popup.dsl').write_text(code,encoding='utf-8')
    # Probe-time discovery nodes have no runtime purpose.
    B.write_graph_dsl(B.get_graph(bp,'EventGraph'),'')
    B.compile_blueprint(bp,True)
    assert assets.save_loaded_asset(bp)
    u.log('CLIENT_HOME_POPUP_BUILD_OK')
    return bp

if __name__=='__main__':
    import toolset_registry
    language=u.InternationalizationLibrary.get_current_language()
    try:
        u.InternationalizationLibrary.set_current_language('en',False)
        from editor_toolset.toolsets.blueprint import _BlueprintCache
        existing=u.load_asset(ROOT+'/UI/WBP_CH_Popup')
        if existing: _BlueprintCache.invalidate(existing)
        with toolset_registry.tool_raising_exceptions():
            build_popup()
    finally:
        u.InternationalizationLibrary.set_current_language(language,False)
