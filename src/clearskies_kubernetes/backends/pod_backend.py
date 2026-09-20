from clearskies_kubernetes.backends.k8s_backend import K8sBackend


class PodBackend(K8sBackend):
    @property
    def api(self):
        if self._api is None:
            self._api = self.client.CoreV1Api()
        return self._api

    @property
    def list_method(self):
        return self.api.list_pod_for_all_namespaces

    @property
    def list_namespaced_method(self):
        return self.api.list_namespaced_pod

    def to_dict(self, record):
        as_dict = super().to_dict(record)

        return {
            **as_dict,
            **{
                "phase": as_dict["status"]["phase"],
                "start_time": as_dict["status"]["start_time"],
                "node_name": as_dict["spec"]["node_name"],
                "name": as_dict["metadata"]["name"],
                "namespace": as_dict["metadata"]["namespace"],
            },
        }
