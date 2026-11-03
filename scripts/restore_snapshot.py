"""Recreate the submission snapshot (including vectors) without re-fetching changing pages."""
import json
from pathlib import Path
from neo4j_client import query
from setup_database import setup
ROOT = Path(__file__).resolve().parents[1]


def restore():
    setup()
    documents = json.loads((ROOT / 'data/snapshot.json').read_text())
    for entry in documents:
        document = entry['document']
        query('MERGE(d:Document {id:$document.id}) SET d += $document '
              'MERGE(country:Country {id:$country_id}) SET country.name=$document.country '
              'MERGE(d)-[:ABOUT_COUNTRY]->(country)',
              {'document': document, 'country_id': 'ES'})
        for chunk in entry['chunks']:
            query('MATCH(d:Document {id:$document_id}) '
                  'MERGE(c:Chunk {id:$chunk.id}) SET c += $chunk '
                  'MERGE(d)-[:HAS_CHUNK]->(c)',
                  {'document_id': document['id'], 'chunk': chunk})
    for embassy in json.loads((ROOT / 'data/embassies.json').read_text()):
        query('MATCH(d:Document {id:$source_id}), (country:Country {id:$country_id}) '
              'MERGE(e:Embassy {id:$embassy.id}) SET e += $embassy '
              'MERGE(d)-[:DOCUMENTS]->(e) MERGE(e)-[:LOCATED_IN]->(country)', embassy)
    query('CALL db.awaitIndexes(120)')
    print(f'Restored {len(documents)} documents and {sum(len(x["chunks"]) for x in documents)} chunks.')


if __name__ == '__main__':
    restore()
