MATCH (c:Chunk)
SEARCH c IN (
  VECTOR INDEX chunk_embedding
  FOR $embedding
  LIMIT 20
) SCORE AS match_score
MATCH (d:Document)-[:HAS_CHUNK]->(c)
WHERE toLower(d.country) = toLower(trim($country))
WITH c, d, match_score,
     match_score + CASE WHEN $topic_hint <> '' AND d.topic = $topic_hint
                        THEN 0.25 ELSE 0 END AS rank_score
ORDER BY rank_score DESC
LIMIT 3
MATCH (d)-[:HAS_CHUNK]->(neighbor:Chunk)
WHERE abs(neighbor.chunk_index - c.chunk_index) <= 1
WITH d, neighbor,
     max(rank_score) AS selection_score,
     max(CASE WHEN neighbor = c THEN match_score ELSE null END) AS vector_score
RETURN neighbor.id AS chunk_id,
       neighbor.chunk_index AS chunk_index,
       neighbor.text AS text,
       d.title AS title,
       d.source_url AS source_url,
       d.retrieved_at AS retrieved_at,
       d.country AS country,
       d.topic AS topic,
       vector_score AS score,
       selection_score,
       CASE WHEN vector_score IS NULL
            THEN 'neighbor' ELSE 'vector'
       END AS retrieved_via
ORDER BY selection_score DESC, source_url, chunk_index;
