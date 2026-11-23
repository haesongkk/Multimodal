import json, urllib.request, sys
from pathlib import Path
ROOT = Path(__file__).parent
def rpc(method, params=None, session=None):
    headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
    if session: headers['Mcp-Session-Id']=session
    data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or {}}).encode()
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/mcp',data,headers),timeout=180) as r:
        raw=r.read().decode()
        if raw.startswith('event:') or raw.startswith('data:'):
            raw=next(l[6:] for l in raw.splitlines() if l.startswith('data: '))
        return json.loads(raw),r.headers.get('Mcp-Session-Id')
def call(name,args):
    _,sid=rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'Codex','version':'1'}})
    return rpc('tools/call',{'name':name,'arguments':args},sid)[0]
if __name__=='__main__':
    if sys.argv[1]=='list':
        _,sid=rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'Codex','version':'1'}})
        result=rpc('tools/list',{},sid)[0]
        (ROOT/'tools.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print([(t['name'],t.get('description','')[:100]) for t in result.get('result',{}).get('tools',[])])
    else:
        print(json.dumps(call(sys.argv[1],json.loads(sys.argv[2])),ensure_ascii=True))
