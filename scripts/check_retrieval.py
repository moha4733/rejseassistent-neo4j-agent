"""Replay the submitted retrieval queries. This is not an agent response generator."""
import argparse
import json
import os
import re
from pathlib import Path
import urllib.request
from neo4j_client import query
ROOT = Path(__file__).resolve().parents[1]


def search(country, question):
    request = urllib.request.Request(os.environ.get('OLLAMA_URL', 'http://localhost:11434') + '/api/embed',
        data=json.dumps({'model':'nomic-embed-text', 'input':'search_query: '+question, 'keep_alive':0}).encode(),
        headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request, timeout=120) as response:
        embedding=json.load(response)['embeddings'][0]
    rows=query((ROOT/'neo4j/vector-retrieval.cypher').read_text(), {'country':country,'embedding':embedding, 'topic_hint': 'mistet_pas' if re.search(r'\bpas\b',question,re.I) and re.search(r'mist|stj[aå]|bortkom',question,re.I) else ''})
    return {'country':country,'question':question,'found':bool(rows),'source_count':len(rows),
            'sources':[{'source_number':i+1,**row} for i,row in enumerate(rows)]}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--country',default='Spanien')
    parser.add_argument('--question',default='Jeg har mistet mit pas. Hvad skal jeg gøre?')
    args=parser.parse_args()
    print(json.dumps(search(args.country,args.question),ensure_ascii=False,indent=2))
