import os
from typing import Any

from neo4j import GraphDatabase


NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USER = os.getenv("NEO4J_USER", "")
NEO4J_PASS = os.getenv("NEO4J_PASS", "")


async def write_entities_and_relationships(text: str) -> None:
    """Minimal example writing a single node for the input text.

    Replace with proper entity extraction and relationship modeling.
    """
    if not (NEO4J_URI and NEO4J_USER and NEO4J_PASS):
        return

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    try:
        with driver.session() as session:
            session.execute_write(_create_document_node, text)
    except Exception:
        # Avoid noisy retries when Neo4j is unreachable in local dev
        return
    finally:
        driver.close()


def _create_document_node(tx, text: str) -> Any:
    return tx.run(
        "MERGE (d:Document {id: $id}) SET d.text = $text RETURN d",
        id=hash(text),
        text=text,
    ).single()


