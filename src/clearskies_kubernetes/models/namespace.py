import clearskies

from clearskies_kubernetes.backends import NamespaceBackend

from . import pod, service


class Namespace(clearskies.Model):
    id_column_name = "name"
    backend = NamespaceBackend()

    name = clearskies.columns.String(validators=[clearskies.validators.Required()])
    context = clearskies.columns.String()
    phase = clearskies.columns.String()
    creation_timestamp = clearskies.columns.Datetime()
    api_version = clearskies.columns.String()
    kind = clearskies.columns.String()
    metadata = clearskies.columns.Json()
    spec = clearskies.columns.Json()
    status = clearskies.columns.Json()

    services = clearskies.columns.HasMany(service.Service, foreign_column_name="namespace")
    pods = clearskies.columns.HasMany(pod.Pod, foreign_column_name="namespace")
