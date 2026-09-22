from typing import Any, Self, overload

import clearskies

from ..helm_release import HelmRelease
from ..namespace import Namespace


class GatewayStatus(clearskies.Column):
    namespaces = clearskies.di.inject.ByClass(Namespace)
    helm_releases = clearskies.di.inject.ByClass(HelmRelease)

    def __init__(self):
        self.is_readable = True
        self.is_writeable = False

    @overload
    def __get__(self, instance: None, cls: type[clearskies.Model]) -> Self:
        pass

    @overload
    def __get__(self, instance: clearskies.Model, cls: type[clearskies.Model]) -> dict[str, Any]:
        pass

    def __get__(self, gateway, cls):
        if gateway is None:
            self.model_class = cls
            return self

        # connect to the k8s cluster
        gateway.cluster.connect()

        return {
            "namespace_created": self.namespaces.find(f"name={gateway.k8s_namespace}").phase == "Active",
            "chart_installed": bool(
                self.helm_releases.where(f"namespace={gateway.k8s_namespace}").find("name=gateway")
            ),
            "auth_method_exists": gateway.has_auth_method(),
            "role_exists": gateway.has_role(),
        }
