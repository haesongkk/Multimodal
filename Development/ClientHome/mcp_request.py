"""One-shot client for the existing LOCAL Unreal MCP endpoint.

Accepts a JSON object on stdin: {"method": "tools/list", "params": {}}.
Uses a new MCP session each time. Never connects to remote hosts.
"""
import json
import sys
import urllib.request


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    request_data = json.load(sys.stdin)
    session = None
    protocol = '2025-03-26'

    def send(method, params, request_id=None):
        nonlocal session
        body = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if request_id is not None:
            body['id'] = request_id
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        if session:
            headers['Mcp-Session-Id'] = session
            headers['MCP-Protocol-Version'] = protocol
        req = urllib.request.Request('http://127.0.0.1:8000/mcp',
                                     data=json.dumps(body).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=120) as response:
            session = response.headers.get('Mcp-Session-Id', session)
            if response.status == 202:
                return None
            if 'text/event-stream' in response.headers.get('Content-Type', ''):
                for line in response:
                    if line.startswith(b'data:'):
                        message = json.loads(line[5:].decode('utf-8'))
                        if message.get('id') == request_id:
                            return message
                raise RuntimeError('MCP stream ended without a matching response')
            payload = response.read()
            return json.loads(payload) if payload else None

    initialized = send('initialize', {'protocolVersion': protocol, 'capabilities': {},
                                     'clientInfo': {'name': 'client-home-local', 'version': '1.0'}}, 1)
    if not initialized or 'error' in initialized:
        raise RuntimeError('MCP initialization failed: ' + str(initialized))
    protocol = initialized['result']['protocolVersion']
    send('notifications/initialized', {})
    response = send(request_data['method'], request_data.get('params', {}), 2)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    if response and 'error' in response:
        sys.exit(1)


if __name__ == '__main__':
    main()
