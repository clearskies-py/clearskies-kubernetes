import clearskies

from clearskies_kubernetes.backends import ServiceBackend


class Service(clearskies.Model):
    id_column_name = "name"
    backend = ServiceBackend()

    name = clearskies.columns.String()
    context = clearskies.columns.String()
    namespace = clearskies.columns.String()
    service_type = clearskies.columns.String()
    cluster_ip = clearskies.columns.String()
    external_ips = clearskies.columns.Json()
    creation_timestamp = clearskies.columns.Datetime()
    ports = clearskies.columns.Json()
    ingress_hostname = clearskies.columns.String()
    api_version = clearskies.columns.String()
    kind = clearskies.columns.String()
    metadata = clearskies.columns.Json()
    spec = clearskies.columns.Json()
    status = clearskies.columns.Json()
