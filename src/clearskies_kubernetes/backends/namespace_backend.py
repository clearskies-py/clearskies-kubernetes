from typing import Any

from clearskies_kubernetes.backends.k8s_backend import K8sBackend


class NamespaceBackend(K8sBackend):
    def __init__(self, can_create=True, can_update=False, can_delete=False, can_query=True):
        super().__init__(can_create=can_create, can_update=can_update, can_delete=can_delete, can_query=can_query)

    @property
    def api(self):
        if self._api is None:
            self._api = self.client.CoreV1Api()
        return self._api

    @property
    def list_method(self):
        return self.api.list_namespace

    @property
    def list_namespaced_method(self):
        raise NotImplementedError("You can't search namespaces by namespace...")

    @property
    def create_method(self):
        return self.api.create_namespace

    @property
    def delete_method(self):
        return self.api.delete_namespace

    def data_to_body(self, data: dict[str, Any]) -> Any:
        return self.client.V1Namespace(metadata=self.client.V1ObjectMeta(name=data["name"]))

    def to_dict(self, record):
        as_dict = super().to_dict(record)

        return {
            **as_dict,
            **{
                "creation_timestamp": as_dict["metadata"]["creation_timestamp"],
                "name": as_dict["metadata"]["name"],
                "phase": as_dict["status"].get("phase"),
            },
        }
