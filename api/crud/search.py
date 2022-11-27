from typing import List
from uuid import UUID

from neo4j import AsyncManagedTransaction, AsyncSession


class SearchCRUD:
    async def search_by_input(
        self, session: AsyncSession, *, words: List[str]
    ) -> List[UUID]:
        async def _search_by_input(
            tx: AsyncManagedTransaction, words: List[str]
        ) -> List[UUID]:
            q = f"""
                MATCH (t:Tag) where t.name in {words}
                WITH collect(t) AS tags
                MATCH (a:Artifact) WHERE ALL(x in tags WHERE (a)--(x))
                return a.id
            """

            result = await tx.run(q)
            values = await result.values()
            scalars = [UUID(value[0]) for value in values]

            return scalars

        return await session.read_transaction(_search_by_input, words)
