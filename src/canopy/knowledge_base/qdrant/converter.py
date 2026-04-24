from copy import deepcopy
from typing import Dict, List, Any, Union
import uuid
from canopy.knowledge_base.models import (
    KBDocChunkWithScore,
    KBEncodedDocChunk,
    KBQuery,
    VectorValues,
)
from pinecone_text.sparse import SparseVector

try:
    from qdrant_client import models
except ImportError:
    pass

from canopy.knowledge_base.qdrant.constants import (
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
    UUID_NAMESPACE,
)


class QdrantConverter:
    @staticmethod
    def convert_id(_id: str) -> str:
        """
        Converts any string into a UUID string based on a seed.

        Qdrant accepts UUID strings and unsigned integers as point ID.
        We use a seed to convert each string into a UUID string deterministically.
        This allows us to overwrite the same point with the original ID.
        """
        return str(uuid.uuid5(uuid.UUID(UUID_NAMESPACE), _id))

    @staticmethod
    def encoded_docs_to_points(
        encoded_docs: List[KBEncodedDocChunk],
    ) -> "List[models.PointStruct]":
        pass

    @staticmethod
    def scored_point_to_scored_doc(
        scored_point,
    ) -> "KBDocChunkWithScore":
        metadata: Dict[str, Any] = deepcopy(scored_point.payload or {})
        _id = metadata.pop("chunk_id")
        text = metadata.pop("text", "")
        document_id = metadata.pop("document_id")
        return KBDocChunkWithScore(
            id=_id,
            text=text,
            document_id=document_id,
            score=scored_point.score,
            source=metadata.pop("source", ""),
            metadata=metadata,
        )

    @staticmethod
    def kb_query_to_search_vector(
        query: KBQuery,
    ) -> "Union[models.NamedVector, models.NamedSparseVector]":
        # Use dense vector if available, otherwise use sparse vector
        query_vector: Union[models.NamedVector, models.NamedSparseVector]
        if query.values:
            query_vector = models.NamedVector(name=DENSE_VECTOR_NAME, vector=query.values)  # noqa: E501
        elif query.sparse_values:
            query_vector = models.NamedSparseVector(
                name=SPARSE_VECTOR_NAME,
                vector=models.SparseVector(
                    indices=query.sparse_values["indices"],
                    values=query.sparse_values["values"],
                ),
            )
        else:
            raise ValueError("Query should have either dense or sparse vector.")
        return query_vector
