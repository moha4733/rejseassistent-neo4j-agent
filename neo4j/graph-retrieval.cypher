MATCH (doc:Document)-[:DOCUMENTS]->(embassy:Embassy)
      -[:LOCATED_IN]->(country:Country)
WHERE toLower(country.name) = toLower(trim($country))
RETURN embassy.name AS embassy,
       embassy.address AS address,
       embassy.city AS city,
       country.name AS country,
       doc.source_url AS source_url,
       embassy.retrieved_at AS retrieved_at
ORDER BY embassy;
