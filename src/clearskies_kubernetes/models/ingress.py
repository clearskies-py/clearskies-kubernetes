import clearskies

from clearskies_kubernetes.backends import IngressBackend


class Ingress(clearskies.Model):
    id_column_name = "name"
    backend = IngressBackend()

    name = clearskies.columns.String()
    namespace = clearskies.columns.String()
    context = clearskies.columns.String()
    class_name = clearskies.columns.String()
    hostname = clearskies.columns.String()
