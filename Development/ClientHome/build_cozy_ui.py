"""Tactile detective journal built in UMG; owns only ClientHome UI assets."""
import unreal as u, json
from pathlib import Path
from editor_toolset.toolsets.object import ObjectTools as O
from editor_toolset.toolsets.blueprint import BlueprintTools as B, _BlueprintCache
ROOT='/Game/ClientHome_Haeso'; OUT=Path(__file__).parent; ART=OUT/'UIArt'
C=(.19,.105,.065); BLUE=(.12,.22,.28); ROSE=(.48,.20,.15)
def build():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
    def import_texture(file,name):
        path=ROOT+'/UI/Cozy/'+name
        tex=u.load_asset(path)
        if not tex:
            task=u.AssetImportTask();task.filename=str(ART/file);task.destination_path=ROOT+'/UI/Cozy';task.destination_name=name;task.automated=True;task.save=True
            u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);tex=u.load_asset(path)
        assert tex,path
        tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_EDITOR_ICON)
        tex.set_editor_property('lod_group',u.TextureGroup.TEXTUREGROUP_UI)
        tex.set_editor_property('mip_gen_settings',u.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        assets.save_loaded_asset(tex)
        return tex
    panel=import_texture('stitched-panel.png','T_StitchedPanel')
    portrait=import_texture('detective-portrait.png','T_DetectivePortrait')
    paw=import_texture('paw-stamp.png','T_PawStamp')
    font=u.load_asset(ROOT+'/UI/Cozy/F_Jua')
    if not font:font=u.AssetToolsHelpers.get_asset_tools().create_asset('F_Jua',ROOT+'/UI/Cozy',u.Font,u.FontFactory())
    O.list_properties(font)
    composite=json.loads(O.get_properties(font,['compositeFont']))['compositeFont']
    composite['defaultTypeface']={'fonts':[{'name':'Regular','font':{'fontFaceAsset':{'refPath':ROOT+'/UI/Cozy/Jua.Jua'}}}]}
    assert O.set_properties(font,json.dumps({'fontCacheType':'Runtime','runtimeFontSource':'Asset','compositeFont':composite}))
    assets.save_loaded_asset(font)
    bp=u.load_asset(ROOT+'/UI/WBP_CH_Popup');_BlueprintCache.invalidate(bp)
    tool=u.get_default_object(u.UMGToolSet)
    items={str(i.widget_name):i for i in tool.call_method('GetWidgets',(bp,)).widgets}
    def read(obj,names):
        schema=json.loads(O.list_properties(obj));assert set(names)<=set(schema),(names,list(schema))
        return json.loads(O.get_properties(obj,names))
    def write(obj,values):
        read(obj,list(values));assert O.set_properties(obj,json.dumps(values,ensure_ascii=False))
    def add(name,cls,parent=None,var=False):
        info=items.get(name)
        if info:
            widget=info.widget
            if parent and widget.get_parent()!=parent:
                widget.remove_from_parent();parent.add_child(widget)
        else:
            info=tool.call_method('AddWidget',(bp,cls.static_class(),name,parent,-1));items[name]=info;widget=info.widget
        if var:tool.call_method('ToggleWidgetAsVariable',(bp,widget,True))
        return widget
    def color(rgb,a=1):return dict(zip(('r','g','b','a'),(*rgb,a)))
    def margin(l,t,r,b):return dict(left=l,top=t,right=r,bottom=b)
    def place(w,x,y,width,height,ax=0,ay=0,alignx=0,aligny=0,z=0):
        write(w.get_editor_property('slot'),{'layoutData':{'anchors':{'minimum':{'x':ax,'y':ay},'maximum':{'x':ax,'y':ay}},'offsets':margin(x,y,width,height),'alignment':{'x':alignx,'y':aligny}},'bAutoSize':False,'zOrder':z})
    def label(name,parent,txt,size=22,rgb=C,var=False):
        w=add(name,u.TextBlock,parent,var)
        f=read(w,['font'])['font'];f.update(fontObject={'refPath':font.get_path_name()},size=size,typefaceFontName='Regular')
        write(w,{'font':f,'text':txt,'autoWrapText':True,'wrappingPolicy':'AllowPerCharacterWrapping','colorAndOpacity':{'specifiedColor':color(rgb),'colorUseRule':'UseColor_Specified'}})
        return w
    def image(name,parent,tex):
        w=add(name,u.Image,parent);read(w,['brush']);w.set_brush_from_texture(tex,False);return w
    def fabric(name,parent):
        w=add(name,u.Border,parent)
        b=read(w,['background'])['background'];b.update(drawAs='Image',resourceObject={'refPath':panel.get_path_name()},imageSize={'x':480,'y':180},margin=margin(.12,.25,.12,.25))
        write(w,{'background':b,'brushColor':color((1,1,1)),'padding':margin(0,0,0,0)})
        return w
    root=add('PopupRoot',u.CanvasPanel)
    # Independent canvas groups keep the journal visible while a clue card opens/closes.
    left=fabric('CozyCaseCard',root);place(left,26,30,470,152)
    lc=add('CozyCaseCanvas',u.CanvasPanel,left)
    face=image('CozyCasePortrait',lc,portrait);place(face,-12,-24,164,164,z=1)
    title=label('CozyCaseTitle',lc,'코코를 찾아서',31,BLUE);place(title,155,38,290,48)
    subtitle=label('CozyCaseSubtitle',lc,'작은 탐정의 첫 번째 의뢰',17);place(subtitle,158,88,285,30)
    right=fabric('CozyJournalCard',root);place(right,-26,30,410,205,ax=1,alignx=1)
    rc=add('CozyJournalCanvas',u.CanvasPanel,right)
    note=label('CozyJournalTitle',rc,'꼬리 끝을 따라',24,BLUE);place(note,34,25,255,38)
    count=label('JournalCount',rc,'0 / 5',26,ROSE,True);place(count,300,25,90,38)
    for i in range(5):
        back=image('PawEmpty'+str(i),rc,paw);place(back,40+i*67,78,49,49)
        write(back,{'colorAndOpacity':color((.65,.48,.32),.22)})
        mark=image('PawFound'+str(i),rc,paw);place(mark,40+i*67,78,49,49)
        tool.call_method('ToggleWidgetAsVariable',(bp,mark,True));write(mark,{'colorAndOpacity':color(ROSE),'renderOpacity':0})
    hint=label('JournalGoal',rc,'단서 다섯 개를 모아 볼까?',18,C,True);place(hint,35,148,350,32)
    # Small bottom control ribbon, separate from the actual investigation prompt.
    keys=fabric('CozyKeys',root);place(keys,28,-22,380,46,ay=1,aligny=1)
    kt=label('CozyKeysText',keys,'WASD  이동하기     E  조사하기',16,BLUE)
    write(kt,{'autoWrapText':False,'wrapTextAt':0,'justification':'Center'})
    write(kt.get_editor_property('slot'),{'padding':margin(18,7,18,7),'horizontalAlignment':'HAlign_Fill','verticalAlignment':'VAlign_Center'})
    prompt=fabric('CozyPrompt',root);tool.call_method('ToggleWidgetAsVariable',(bp,prompt,True));place(prompt,0,-28,690,80,ax=.5,ay=1,alignx=.5,aligny=1)
    hinttxt=label('JournalPrompt',prompt,'코코가 남긴 흔적을 찾아보자.',22,C,True)
    write(hinttxt,{'autoWrapText':False,'wrapTextAt':0,'justification':'Center'})
    write(hinttxt.get_editor_property('slot'),{'padding':margin(36,20,28,16),'horizontalAlignment':'HAlign_Fill','verticalAlignment':'VAlign_Center'})
    # Plush clue dialogue with a real illustrated portrait and room for long Korean text.
    card=fabric('PopupCard',root);tool.call_method('ToggleWidgetAsVariable',(bp,card,True))
    write(card.get_editor_property('slot'),{'layoutData':{'anchors':{'minimum':{'x':.13,'y':.92},'maximum':{'x':.87,'y':.92}},'offsets':margin(0,0,0,0),'alignment':{'x':0,'y':1}},'bAutoSize':True,'zOrder':10})
    row=add('CozyPopupRow',u.HorizontalBox,card)
    for child in list(row.get_all_children()):
        if child.get_name().startswith('TRASH_') or child.get_name()=='PopupContent':row.remove_child(child)
    portraitbox=add('CozyPopupPortraitBox',u.SizeBox,row);O.list_properties(portraitbox);portraitbox.set_width_override(190);portraitbox.set_height_override(210)
    image('CozyPopupPortrait',portraitbox,portrait)
    write(portraitbox.get_editor_property('slot'),{'padding':margin(20,8,0,8),'verticalAlignment':'VAlign_Bottom'})
    content=add('CozyPopupText',u.VerticalBox,row)
    write(content.get_editor_property('slot'),{'size':{'value':1,'sizeRule':'Fill'},'padding':margin(20,30,42,26),'verticalAlignment':'VAlign_Center'})
    # Reorder the retained fields without invalidating the HUD's widget reference.
    for name,txt,size,col,pad in [
        ('PopupEyebrow','',16,ROSE,0),
        ('PopupTitle','코코는 어디로 갔을까?',30,BLUE,12),
        ('PopupMessage','집 안에 남은 다섯 가지 흔적을 찾아보자.',22,C,18),
        ('PopupHint','[Space]',17,ROSE,0)]:
        w=label(name,content,txt,size,col,True)
        write(w.get_editor_property('slot'),{'padding':margin(0,0,0,pad)})
        if name=='PopupEyebrow':write(w,{'visibility':'Collapsed'})
        if name=='PopupHint':
            write(w,{'justification':'Right','autoWrapText':False})
            write(w.get_editor_property('slot'),{'horizontalAlignment':'HAlign_Fill','padding':margin(0,0,34,12)})
    write(root,{'visibility':'HitTestInvisible'})
    assert tool.call_method('CompileWidgetBlueprint',(bp,))
    B.compile_blueprint(bp)
    def node(g,term,prefix=None):
        ids=sorted(set(i for i in B.find_node_types(g,term) if i.split('|')[-1]==term and (not prefix or i.startswith(prefix))))
        assert len(ids)==1,(term,ids)
        B.get_node_type_pins(g,ids[0]);return ids[0]
    g=B.get_graph(bp,'Present')
    text=node(g,'SetText(Text)')
    vis=next(i for i in B.find_node_types(g,'SetVisibility') if i.split('|')[-1]=='SetVisibility' and any(p.name=='InVisibility' for p in B.get_node_type_pins(g,i).input_pins))
    getter=lambda name:'('+node(g,'Get'+name,'Variables|')+')'
    lines=[f'({text} :self {getter(n)} :InText {value})' for n,value in [('PopupTitle','Heading'),('PopupMessage','Body'),('PopupHint','(select Finished "[Esc]" "[Space]")')]]
    lines += [f'({vis} :self self :InVisibility "HitTestInvisible")',f'(if Shown ({vis} :self {getter("PopupCard")} :InVisibility "HitTestInvisible") ({vis} :self {getter("CozyPrompt")} :InVisibility "Collapsed") (else ({vis} :self {getter("PopupCard")} :InVisibility "Collapsed") ({vis} :self {getter("CozyPrompt")} :InVisibility "HitTestInvisible")))']
    code='(fn Present (Heading Body Shown Finished)\n'+'\n'.join(lines)+')'
    B.write_graph_dsl(g,code);(OUT/'WBP_CH_Popup.dsl').write_text(code,encoding='utf-8')
    g=B.add_function_graph(bp,'UpdateJournal')
    for n,t in [('Found','int'),('Hint','text'),('Solved','bool')]:
        if not B._param_name_exists(g,n,True):B.add_function_param(g,n,t,True)
    B.compile_blueprint(bp)
    text=node(g,'SetText(Text)');opacity=node(g,'SetRenderOpacity','Widget|')
    count='"5 / 5"'
    for i in reversed(range(5)):count=f'(select (== Found {i}) "{i} / 5" {count})'
    lines=[f'({text} :self {getter("JournalCount")} :InText {count})',f'({text} :self {getter("JournalPrompt")} :InText Hint)',f'({text} :self {getter("JournalGoal")} :InText (select Solved "코코의 길을 찾았어! 현관으로 가자." "단서 다섯 개를 모아 볼까?"))']
    for i in range(5):lines.append(f'({opacity} :self {getter("PawFound"+str(i))} :InOpacity (select (> Found {i}) 1.0 0.0))')
    code='(fn UpdateJournal (Found Hint Solved)\n'+'\n'.join(lines)+')'
    B.write_graph_dsl(g,code);(OUT/'WBP_CH_UpdateJournal.dsl').write_text(code,encoding='utf-8')
    B.write_graph_dsl(B.get_graph(bp,'EventGraph'),'')
    B.compile_blueprint(bp,True);assert assets.save_loaded_asset(bp)
    u.log('COZY_UI_BUILD_OK')
    return bp
if __name__=='__main__':
    import toolset_registry
    lang=u.InternationalizationLibrary.get_current_language()
    try:
        u.InternationalizationLibrary.set_current_language('en',False)
        with toolset_registry.tool_raising_exceptions():build()
    finally:u.InternationalizationLibrary.set_current_language(lang,False)
