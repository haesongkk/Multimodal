"""Keep completed investigations pointing toward the exit in the bottom journal."""
def configure(hud,B):
 g=B.get_graph(hud,'SyncJournal')
 ids=[n for n in B.find_node_types(g,'UpdateJournal') if n.endswith('|UpdateJournal')]
 assert len(ids)==1,ids
 B.get_node_type_pins(g,ids[0])
 def get(n):
  matches=[x for x in B.find_node_types(g,'Get'+n) if x.startswith('Variables|') and x.endswith('|Get'+n)]
  assert len(matches)==1,matches
  B.get_node_type_pins(g,matches[0])
  return '('+matches[0]+')'
 hint=f'(select (>= {get("Count")} 5) (select (== {get("Nearby")} 4) "[E] 현관문 열고 나가기" "코코의 길을 찾았어! 현관으로 나가 보자.") {get("Prompt")})'
 code=f'(fn SyncJournal () ({ids[0]} :self {get("PopupUI")} :Found {get("Count")} :Hint {hint} :Solved {get("Deduced")}))'
 B.write_graph_dsl(g,code)
