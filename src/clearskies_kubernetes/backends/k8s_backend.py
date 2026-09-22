from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import clearskies
from clearskies.query.result import (
    CountQueryResult,
    RecordQueryResult,
    RecordsQueryResult,
    SuccessQueryResult,
)
from kubernetes import client, config

if TYPE_CHECKING:
    from clearskies import Model
    from clearskies.autodoc.schema import Schema as AutoDocSchema
    from clearskies.autodoc.schema import String as AutoDocString
    from clearskies.query import Query


class K8sBackend(clearskies.backends.Backend):
    _api = None
    _client = None
    config_loaded = False

    def __init__(self, can_create=False, can_update=False, can_delete=False, can_query=True):
        super().__init__(can_create=can_create, can_update=can_update, can_delete=can_delete, can_query=can_query)

    @property
    def client(self):
        if not self.__class__.config_loaded:
            config.load_kube_config()
            self.__class__.config_loaded = True
        return client

    @property
    def api(self):
        raise NotImplementedError(f"Extending backend {self.__class__} did not implement self.api")

    @property
    def list_method(self):
        raise NotImplementedError(
            f"Extending backend {self.__class__} did not implement self.list_method and so query operations are disallowed"
        )

    @property
    def list_namespaced_method(self):
        raise NotImplementedError(
            f"Extending backend {self.__class__} did not implement self.list_namespaced_method and so query operations are disallowed"
        )

    @property
    def create_method(self):
        raise NotImplementedError(
            f"Extending backend {self.__class__} did not implement self.create_method and so create operations are disallowed"
        )

    @property
    def delete_method(self):
        raise NotImplementedError(
            f"Extending backend {self.__class__} did not implement self.delete_method and so delete operations are disallowed"
        )

    @property
    def update_method(self):
        raise NotImplementedError(
            f"Extending backend {self.__class__} did not implement self.update_method and so update operations are disallowed"
        )

    def to_dict(self, record):
        as_dict = record.to_dict()

        return {
            "api_version": as_dict["api_version"],
            "kind": as_dict["kind"],
            "metadata": as_dict["metadata"],
            "spec": as_dict["spec"],
            "status": as_dict["status"],
        }

    def data_to_body(self, data: dict[str, Any]) -> Any:
        raise NotImplementedError()

    def update(self, id: int | str, data: dict[str, Any], model: Model) -> RecordQueryResult:
        """Update the record with the given id with the information from the data dictionary."""
        raise NotImplementedError()

    def create(self, data: dict[str, Any], model: Model) -> RecordQueryResult:
        """Create a record with the information from the data dictionary."""
        self.create_method(body=self.data_to_body(data))

        records_response = self.records(
            clearskies.query.Query(
                model.__class__,
                conditions=[clearskies.query.ParsedCondition(model.id_column_name, "=", [data[model.id_column_name]])],
            )
        )
        records = records_response.data
        return RecordQueryResult(record=records[0])

    def delete(self, id: int | str, model: Model) -> SuccessQueryResult:
        """Delete the record with the given id."""
        self.delete_method(name=model.name)  # ty: ignore[unresolved-attribute]
        return SuccessQueryResult()

    def records(self, query: Query) -> RecordsQueryResult:
        """
        Return a list of records that match the given query configuration.

        The QueryResult includes next_page_data for pagination information.
        """
        namespace = ""
        context = ""
        kwargs = {}
        search_conditions = {}
        for condition in query.conditions:
            if condition.operator != "=":
                raise ValueError("The k8s backend only supports searching by the equals operator")

            if condition.column_name == "namespace":
                namespace = condition.values[0]
            elif condition.column_name == "label":
                kwargs["label_selector"] = condition.values[0]
            elif condition.column_name == "field":
                kwargs["field_selector"] = condition.values[0]
            elif condition.column_name == "context":
                context = condition.values[0]
            else:
                search_conditions[condition.column_name] = condition.values[0]

        if query.pagination.get("continue"):
            kwargs["_continue"] = query.pagination.get("continue")

        if context:
            config.load_kube_config(context=context)

        if namespace:
            results = self.list_namespaced_method(namespace=namespace, **kwargs)
        else:
            results = self.list_method(**kwargs)
        records = []
        for item in results.items:
            record = self.to_dict(item)
            if not self.record_matches_search_conditions(record, search_conditions):
                continue
            records.append(record)

        return RecordsQueryResult(
            records,
            next_page_data={"continue": results.metadata._continue} if results.metadata._continue else {},
        )

    def record_matches_search_conditions(self, record, search_conditions):
        for key, value in search_conditions.items():
            if key not in record:
                raise ValueError(
                    f"Attempted to search by {key} via backend {self.__class__.__name__} but one of the records I received back doesn't have that key present"
                )

            if record[key] != value:
                return False

        return True

    def count(self, query: Query) -> CountQueryResult:
        res = self.records(query)
        return CountQueryResult(count=len(res.records))

    def validate_pagination_data(self, data: dict[str, Any], case_mapping: Callable[[str], str]) -> str:
        return ""

    def allowed_pagination_keys(self) -> list[str]:
        return ["continue"]

    def documentation_pagination_next_page_response(self, case_mapping: Callable) -> list[Any]:
        return [AutoDocString(case_mapping("continue"), example="...")]

    def documentation_pagination_parameters(self, case_mapping: Callable) -> list[tuple[AutoDocSchema, str]]:
        return [
            (
                AutoDocString(case_mapping("continue"), example="..."),
                "The continue token for the next page of results",
            )
        ]

    def documentation_pagination_next_page_example(self, case_mapping: Callable) -> dict[str, Any]:
        return {case_mapping("continue"): ""}
