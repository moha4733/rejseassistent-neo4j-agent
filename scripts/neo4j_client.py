"""Small standard-library client for Neo4j Query API v2. No credentials in source."""
import base64
import json
import os
import urllib.error
import urllib.request


def query(statement, parameters=None):
    base = os.environ.get('NEO4J_URL', 'http://localhost:7474').rstrip('/')
    database = os.environ.get('NEO4J_DATABASE', 'rejseassistent')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ['NEO4J_PASSWORD']
    request = urllib.request.Request(
        f'{base}/db/{database}/query/v2',
        data=json.dumps({'statement': statement, 'parameters': parameters or {}}).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Basic ' +
                 base64.b64encode(f'{user}:{password}'.encode()).decode()})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode()) from None
    if result.get('errors'):
        raise RuntimeError(json.dumps(result['errors'], ensure_ascii=False))
    return [dict(zip(result['data']['fields'], row)) for row in result['data']['values']]
