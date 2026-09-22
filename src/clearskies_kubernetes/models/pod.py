import clearskies

from clearskies_kubernetes.backends import PodBackend


class Pod(clearskies.Model):
    id_column_name = "name"
    backend = PodBackend()

    name = clearskies.columns.String()
    context = clearskies.columns.String()
    namespace = clearskies.columns.String()
    phase = clearskies.columns.String()
    start_time = clearskies.columns.Datetime()
    node_name = clearskies.columns.String()
    api_version = clearskies.columns.String()
    kind = clearskies.columns.String()
    metadata = clearskies.columns.Json()
    spec = clearskies.columns.Json()
    status = clearskies.columns.Json()
