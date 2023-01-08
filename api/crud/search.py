from typing import List
from uuid import UUID

from neo4j import AsyncManagedTransaction, AsyncSession


class SearchCRUD:
    async def search_by_input(
        self, session: AsyncSession, *, words: List[str], skip: int, limit: int
    ) -> List[UUID]:
        async def _search_by_input(tx: AsyncManagedTransaction) -> List[UUID]:
            q = f"""
                MATCH (t:Tag) where t.name in {words}
                WITH collect(t) AS tags
                MATCH (a:Artifact) WHERE ALL(x in tags WHERE (a)--(x))
                return a.id
                SKIP {skip}
                LIMIT {limit}
            """

            result = await tx.run(q)
            values = await result.values()
            scalars = [UUID(value[0]) for value in values]

            return scalars

        return await session.read_transaction(_search_by_input)

    async def apply_search(
        self, session: AsyncSession, *, words: List[str], ids: List[UUID]
    ) -> None:  # TODO: refactor and move from artifact search to execution search
        async def _apply_search(tx: AsyncManagedTransaction, artifact_id: UUID) -> None:
            q = 'CREATE (a:Artifact {id: "%s"})\n' % str(artifact_id)
            for i, word in enumerate(words):
                q += 'MERGE (t%i:Tag {name: "%s"}) CREATE (a)-[:HAVE]->(t%i)\n' % (
                    i,
                    word,
                    i,
                )

            await tx.run(q)

        for artifact_id in ids:
            await session.execute_write(_apply_search, artifact_id)

    async def infinity_search(
        self, session: AsyncSession, *, seed: float, skip: int, limit: int
    ) -> List[UUID]:
        async def _infinity_search(tx: AsyncManagedTransaction) -> List[UUID]:
            q = f"""
                MATCH (a:Artifact)
                RETURN a.id
                SKIP {skip}
                LIMIT {limit}
            """

            result = await tx.run(q)
            values = await result.values()
            scalars = [UUID(value[0]) for value in values]

            return scalars

        return await session.read_transaction(_infinity_search)
