from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

import clearskies
from clearskies.query import ParsedCondition, Query
from clearskies.query.result import (
    RecordQueryResult,
    RecordsQueryResult,
)

from .helm_backend import HelmBackend

if TYPE_CHECKING:
    import clearskies_kubernetes.models


class HelmReleaseBackend(HelmBackend):
    async def to_dict(self, release):
        current_revision = await release.current_revision()
        return {
            "name": release.name,
            "namespace": release.namespace,
            "current_revision_number": current_revision.revision,
            "status": current_revision.status.value,
            "current_revision_object": current_revision,
            "release_object": release,
        }

    async def records_async(self, query: clearskies.query.Query) -> RecordsQueryResult:
        kwargs = {"all_namespaces": True, "all": True}
        name = ""
        context = ""
        for condition in query.conditions:
            if condition.operator != "=":
                raise ValueError("The helm backend only supports searching by the equals operator")

            if condition.column_name == "namespace":
                kwargs["namespace"] = condition.values[0]
                kwargs["all_namespaces"] = False
            elif condition.column_name == "name":
                name = condition.values[0]
            elif condition.column_name == "context":
                context = condition.values[0]
            else:
                raise KeyError(
                    f"The helm backend only supports searching by namespace and release name, not {condition.column_name}"
                )

        if context:
            self.set_context(context)

        if query.sorts:
            raise ValueError("The helm backend does not support sorting.")

        releases = await self.client.list_releases(**kwargs)
        records = []
        for release in releases:
            if name and release.name != name:
                continue

            as_dict = await self.to_dict(release)
            records.append(as_dict)

        return RecordsQueryResult(
            records,
            next_page_data={},
        )

    async def deploy_async(
        self,
        name: str,
        namespace: str,
        chart_url: str,
        chart_name: str,
        values: dict[str, Any],
        version: str | None = None,
    ) -> None:
        chart = await self.client.get_chart(
            chart_name,
            repo=chart_url,
            version=version,
        )

        await self.client.install_or_upgrade_release(
            name,
            chart,
            values,
            namespace=namespace,
            atomic=True,
        )

    def create(self, data: dict[str, Any], model: clearskies.Model) -> RecordQueryResult:
        for required_key in ["name", "namespace", "values", "chart_url", "chart_name"]:
            if required_key not in data:
                raise KeyError(f"I cannot install a chart without '{required_key}'")

        context = data.get("context")
        if context:
            self.set_context(context)

        asyncio.run(
            self.deploy_async(
                data["name"],
                data["namespace"],
                data["chart_url"],
                data["chart_name"],
                data["values"] if isinstance(data["values"], dict) else json.loads(data["values"]),
            )
        )

        records_response = self.records(
            Query(
                model.__class__,
                conditions=[
                    ParsedCondition("name", "=", [data["name"]]),
                    ParsedCondition("namespace", "=", [data["namespace"]]),
                ],
            )
        )
        return RecordQueryResult(record=records_response.data[0])

    def update(
        self,
        id: int | str,
        data: dict[str, Any],
        model: clearskies_kubernetes.models.HelmRelease,
    ) -> RecordQueryResult:  # ty: ignore[invalid-method-override]
        for required_key in ["values", "chart_url", "chart_name"]:
            if required_key not in data:
                raise KeyError(f"I cannot update a chart without '{required_key}'")

        context = data.get("context")
        if context:
            self.set_context(context)

        asyncio.run(
            self.deploy_async(
                model.name,
                model.namespace,
                data["chart_url"],
                data["chart_name"],
                data["values"] if isinstance(data["values"], dict) else json.loads(data["values"]),
            )
        )

        records_response = self.records(
            Query(
                model.__class__,
                conditions=[
                    ParsedCondition("name", "=", [model.name]),
                    ParsedCondition("namespace", "=", [model.namespace]),
                ],
            )
        )
        return RecordQueryResult(record=records_response.data[0])
