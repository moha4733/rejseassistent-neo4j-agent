"""Create constraints/index in an existing database. Does not erase existing data."""
from pathlib import Path
from neo4j_client import query
ROOT = Path(__file__).resolve().parents[1]


def setup():
    for statement in (ROOT / 'neo4j/schema.cypher').read_text().split(';'):
        if statement.strip():
            query(statement)
    query('CALL db.awaitIndexes(120)')


if __name__ == '__main__':
    setup()
    print('Database constraints and vector index are ready.')
