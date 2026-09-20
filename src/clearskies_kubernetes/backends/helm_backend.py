from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable

import clearskies
from clearskies.query.result import (
    CountQueryResult,
    RecordQueryResult,
    RecordsQueryResult,
    SuccessQueryResult,
)
from pyhelm3 import Client

if TYPE_CHECKING:
    from clearskies import Model
    from clearskies.autodoc.schema import Schema as AutoDocSchema
    from clearskies.query import Query


class HelmBackend(clearskies.backends.Backend):
    _client = None

    @property
    def client(self):
        if not self._client:
            self._client = Client()
        return self._client

    def set_context(self, context):
        self._client = Client(kubecontext=context)

    async def records_async(self, query: clearskies.query.Query) -> RecordsQueryResult:
        raise NotImplementedError()

    def records(self, query: clearskies.query.Query) -> RecordsQueryResult:
        """
        Return a list of records that match the given query configuration.

        The QueryResult includes next_page_data for pagination information.
        """
        return asyncio.run(self.records_async(query))

    def count(self, query: Query) -> CountQueryResult:
        res = self.records(query)
        return CountQueryResult(count=len(res.records))

    def validate_pagination_data(self, data: dict[str, Any], case_mapping: Callable[[str], str]) -> str:
        raise ValueError("The helm backend does not support pagination")

    def allowed_pagination_keys(self) -> list[str]:
        return []

    def documentation_pagination_next_page_response(self, case_mapping: Callable) -> list[Any]:
        return []

    def documentation_pagination_parameters(self, case_mapping: Callable) -> list[tuple[AutoDocSchema, str]]:
        return []

    def documentation_pagination_next_page_example(self, case_mapping: Callable) -> dict[str, Any]:
        return {}

    def update(self, id: int | str, data: dict[str, Any], model: Model) -> RecordQueryResult:
        """Update the record with the given id with the information from the data dictionary."""
        raise NotImplementedError()

    def create(self, data: dict[str, Any], model: Model) -> RecordQueryResult:
        """Create a record with the information from the data dictionary."""
        raise NotImplementedError()

    def delete(self, id: int | str, model: Model) -> SuccessQueryResult:
        """Delete the record with the given id."""
        raise NotImplementedError()
