"""Validate public submission artifacts; optionally verify a restored/live Neo4j database."""
import argparse
import datetime
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(live=False):
    checks = []
    def check(name, condition, details=None):
        if not condition:
            raise AssertionError(name + ': ' + str(details))
        checks.append({'check': name, 'passed': True, 'details': details})

    snapshot = json.loads((ROOT/'data/snapshot.json').read_text())
    docs = [entry['document'] for entry in snapshot]
    chunks = [chunk for entry in snapshot for chunk in entry['chunks']]
    check('snapshot_document_ids_unique', len({d['id'] for d in docs}) == 3)
    check('snapshot_chunk_ids_unique', len({c['id'] for c in chunks}) == len(chunks) == 20)
    check('embedding_dimensions_and_finite_values', all(len(c['embedding']) == 768 and
          all(isinstance(v, (int,float)) and math.isfinite(v) for v in c['embedding']) for c in chunks))
    check('source_urls_official_https', all(re.fullmatch(r'https://um\.dk/[^\s<>"\']+', d['source_url']) for d in docs))
    for entry in snapshot:
        indices = sorted(c['chunk_index'] for c in entry['chunks'])
        check('contiguous_chunks_' + entry['document']['id'], indices == list(range(len(indices))))
    for path in sorted((ROOT/'workflows').glob('*.json')):
        workflow = json.loads(path.read_text())
        check(path.name+'_no_pin_data', not workflow.get('pinData'))
        for node in workflow['nodes']:
            for credential in node.get('credentials', {}).values():
                check(path.name+'_credential_placeholder', credential['id'] == 'REPLACE_WITH_YOUR_CREDENTIAL_ID')
        triggers = [n for n in workflow['nodes'] if n['type'].endswith('executeWorkflowTrigger')]
        if triggers:
            params=triggers[0]['parameters']
            check(path.name+'_explicit_input_schema',params.get('inputSource')=='jsonExample' and 'country' in json.loads(params['jsonExample']))
    traces = [json.loads(p.read_text()) for p in sorted((ROOT/'examples/raw').glob('0[123]-*.json'))]
    check('three_actual_agent_traces', len(traces)==3 and all(t['status']=='success' for t in traces))
    check('three_actual_answers', all(any(e['type']=='text' and e['content'].strip() for e in t['timeline']) for t in traces))
    japan = next(t for t in traces if t['question'].find('Japan')>=0)
    calls=[e for e in japan['timeline'] if e['type']=='tool-call']
    check('japan_tool_inputs', bool(calls) and all(e['input']['country']=='Japan' for e in calls))
    results=[r for e in calls for rows in e['output']['data'].values() for r in rows]
    check('japan_actual_tools_return_no_sources', all(r['found'] is False for r in results))
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text()):
            if '://' not in target and not target.startswith('#'):
                check('local_link_'+str(path.relative_to(ROOT))+':'+target,(path.parent/target.split('#')[0]).exists())
    if live:
        from neo4j_client import query
        from check_retrieval import search
        nodes=query('MATCH(n) RETURN labels(n)[0] AS label,count(*) AS count')
        check('live_node_counts',{r['label']:r['count'] for r in nodes} == {'Country':1,'Document':3,'Chunk':20,'Embassy':1},nodes)
        rels=query('MATCH()-[r]->() RETURN type(r) AS type,count(*) AS count')
        check('live_relationship_counts',{r['type']:r['count'] for r in rels} == {'ABOUT_COUNTRY':3,'HAS_CHUNK':20,'DOCUMENTS':1,'LOCATED_IN':1},rels)
        idx=query("SHOW INDEXES YIELD name,state WHERE name='chunk_embedding' RETURN name,state")
        check('live_vector_index_online', len(idx)==1 and idx[0]['state']=='ONLINE',idx)
        constraints=query('SHOW CONSTRAINTS YIELD name RETURN name')
        check('live_unique_constraints',{'document_id_unique','chunk_id_unique','country_id_unique','embassy_id_unique'}.issubset({r['name'] for r in constraints}))
        graph=query((ROOT/'neo4j/graph-retrieval.cypher').read_text(),{'country':'Spanien'})
        check('live_graph_address',len(graph)==1 and graph[0]['embassy']=='Danmarks ambassade i Spanien' and 'Calle Serrano' in graph[0]['address'])
        check('live_graph_japan_empty',not query((ROOT/'neo4j/graph-retrieval.cypher').read_text(),{'country':'Japan'}))
        for question in ['Jeg har mistet mit pas. Hvad skal jeg gøre?','hvad skal jeg gøre hvis jeg har mistet mit pas?']:
            result=search('Spanien',question)
            check('live_passport_recall_'+question,{'es-mistet-pas-0','es-mistet-pas-1'}.issubset({s['chunk_id'] for s in result['sources']}))
            check('live_sources_correct_country',all(s['country']=='Spanien' for s in result['sources']))
        check('live_vector_japan_empty',search('Japan','Jeg har mistet mit pas. Hvad skal jeg gøre?')['found'] is False)
    return {'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'live':live,
            'passed':True,'check_count':len(checks),'checks':checks}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=validate(args.live)
    if args.output:
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f"Passed {report['check_count']} checks (live={args.live}).")
