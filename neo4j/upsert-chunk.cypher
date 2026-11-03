MERGE (country:Country {id: $country_id})
SET country.name = $country
MERGE (d:Document {id: $source_id})
SET d.title=$title, d.source_url=$source_url, d.country=$country,
    d.topic=$topic, d.publisher=$publisher, d.retrieved_at=$retrieved_at
MERGE (d)-[:ABOUT_COUNTRY]->(country)
FOREACH (_ IN CASE WHEN $embassy_address IS NULL THEN [] ELSE [1] END |
  MERGE (e:Embassy {id:$embassy_id})
  SET e.name=$embassy_name, e.address=$embassy_address, e.city=$embassy_city,
      e.source_url=$source_url, e.retrieved_at=$retrieved_at
  MERGE (e)-[:LOCATED_IN]->(country)
  MERGE (d)-[:DOCUMENTS]->(e)
)
MERGE (c:Chunk {id:$chunk_id})
SET c.text=$chunk_text, c.chunk_index=$chunk_index, c.embedding=$embedding,
    c.embedding_model=$embedding_model, c.embedding_dimensions=$embedding_dimensions
MERGE (d)-[:HAS_CHUNK]->(c)
WITH d,c
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(stale:Chunk)
WHERE stale.chunk_index >= $chunk_count
WITH d,c,collect(stale) AS staleChunks
FOREACH (old IN staleChunks | DETACH DELETE old)
RETURN d.id AS source_id,c.id AS chunk_id,size(c.embedding) AS dimensions;
