import clearskies
from clearskies.query.result import (
    RecordsQueryResult,
)

from .helm_backend import HelmBackend


class HelmRevisionBackend(HelmBackend):
    async def to_dict(self, revision):
        current_revision = await revision.release.current_revision()
        return {
            "revision_number": revision.revision,
            "release_name": revision.release.name,
            "namespace": revision.release.namespace,
            "is_latest": current_revision.revision == revision.revision,
            "status": revision.status.value,
            "updated": revision.updated,
            "description": revision.description,
            "notes": revision.notes,
            "release_object": revision.release,
            "revision_object": revision,
        }

    async def records_async(self, query: clearskies.query.Query) -> RecordsQueryResult:
        """
        Return a list of records that match the given query configuration.

        The QueryResult includes next_page_data for pagination information.
        """
        is_latest = False
        release_name = ""
        namespace = ""
        name = ""
        release_number = 0
        for condition in query.conditions:
            if condition.operator != "=":
                raise ValueError("The helm backend only supports searching by the equals operator")

            if condition.column_name == "namespace":
                namespace = condition.values[0]
            elif condition.column_name == "release_name":
                release_name = condition.values[0]
            elif condition.column_name == "is_latest":
                is_latest = True
            elif condition.column_name == "revision_number":
                release_number = int(condition.values[0])
            elif condition.column_name == "context":
                context = condition.values[0]
            else:
                raise KeyError("The helm backend only supports searching by namespace and release name")

        if context:
            self.set_context(context)

        if query.sorts:
            raise ValueError("The helm backend does not support sorting.")

        if release_number and is_latest:
            raise ValueError(
                "Both release_number and is_latest were specified as search conditions: these are mutual exclusive"
            )

        if not release_name or not namespace:
            raise ValueError("To search for a revision you must query by both the release name and the namespace")

        # if we are explicitly searching for the latest revision then we can find it directly,
        # but otherwise we have to first fetch the specific release.
        if is_latest:
            revision = await self.client.get_current_revision(release_name, namespace=namespace)
            as_dict = await self.to_dict(revision)
            return RecordsQueryResult([as_dict], next_page_data={})

        # for a specific revision (or all of them for a release) we have to first find the release and search
        # through it's revisions.  The only way to find a release is by listing all of them and searchin by name.
        records = []
        releases = await self.client.list_releases(all=True, namespace=namespace)
        for release in releases:
            if release.name != release_name:
                continue

            if release_number:
                revision = await release.revision(release_number)
                as_dict = await self.to_dict(revision)
                records.append(as_dict)
            else:
                revisions = await release.history()
                records.extend([await self.to_dict(revision) for revision in revisions])
            break

        return RecordsQueryResult(
            records,
            next_page_data={},
        )
