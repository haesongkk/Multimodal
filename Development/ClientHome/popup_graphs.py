"""Compiled HUD -> UMG presentation bridge, no editor Python at runtime."""
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as B

def install_popup_graphs(hud, popup):
    def pin(node,name,output=False):
        info=B.get_node_infos([node])[0]
        pins=info.output_pins if output else info.input_pins
        return next(p.pin_id for p in pins if p.name==name)
    def link(a,ap,b,bp): B.connect_pins(pin(a,ap,True),pin(b,bp))
    def value(n,p,v): B.set_pin_value(pin(n,p),v)
    def node(g,term,prefix=None):
        ids=sorted(set(i for i in B.find_node_types(g,term) if i.split('|')[-1]==term and (not prefix or i.startswith(prefix))))
        assert len(ids)==1,(term,ids)
        B.get_node_type_pins(g,ids[0])
        return B.create_node(g,ids[0],u.IntPoint(0,0))
    def function(name):
        g=B.add_function_graph(hud,name)
        B.write_graph_dsl(g,'(fn '+name+' ())')
        editor=u.BlueprintGraphEditor.get_graph_editor(g)
        entry=next(n for n in editor.list_all_nodes() if isinstance(n,u.K2Node_FunctionEntry))
        return g,editor,entry
    g,e,entry=function('InitPopup')
    create=e.add_call_function_node('/Script/UMG.WidgetBlueprintLibrary:Create')
    value(create,'WidgetType',popup.generated_class().get_path_name())
    own=node(g,'GetOwningPlayerController','HUD|')
    link(own,'ReturnValue',create,'OwningPlayer')
    cast=node(g,'CastToWBP_CH_Popup','Utilities|Casting|')
    link(entry,'then',create,'execute'); link(create,'then',cast,'execute')
    link(create,'ReturnValue',cast,'Object')
    cast_out=next(p.name for p in B.get_node_infos([cast])[0].output_pins if p.name.startswith('As'))
    setter=node(g,'SetPopupUI','Variables|')
    link(cast,'then',setter,'execute'); link(cast,cast_out,setter,'PopupUI')
    add=e.add_call_function_node('/Script/UMG.UserWidget:AddToViewport')
    link(setter,'then',add,'execute'); link(cast,cast_out,add,'self')
    value(add,'ZOrder','10')
    B.compile_blueprint(hud,True)
    g,e,entry=function('RefreshPopup')
    present=e.add_call_function_node(popup.generated_class().get_path_name()+':Present')
    link(entry,'then',present,'execute')
    for variable,target in [('PopupUI','self'),('Title','Heading'),('Message','Body'),('Popup','Shown'),('Complete','Finished')]:
        getter=node(g,'Get'+variable,'Variables|')
        link(getter,variable,present,target)
    B.compile_blueprint(hud,True)
