from clearskies_kubernetes.backends.k8s_backend import K8sBackend


class IngressBackend(K8sBackend):
    @property
    def api(self):
        if self._api is None:
            self._api = self.client.NetworkingV1Api()
        return self._api

    @property
    def list_method(self):
        return self.api.list_ingress_for_all_namespaces

    @property
    def list_namespaced_method(self):
        return self.api.list_namespaced_ingress

    def to_dict(self, record):
        as_dict = super().to_dict(record)

        load_balancer = as_dict["status"].get("load_balancer")
        ingress_hostname = ""
        if load_balancer and load_balancer.get("ingress"):
            for ingress in load_balancer.get("ingress"):
                if "hostname" in ingress:
                    ingress_hostname = ingress["hostname"]

        return {
            **as_dict,
            **{
                "creation_timestamp": as_dict["metadata"]["creation_timestamp"],
                "name": as_dict["metadata"]["name"],
                "namespace": as_dict["metadata"]["namespace"],
                "class_name": as_dict["spec"]["ingress_class_name"],
                "hostname": ingress_hostname,
            },
        }
