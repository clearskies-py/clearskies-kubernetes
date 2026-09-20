import clearskies

from clearskies_kubernetes.backends import HelmReleaseBackend

from . import helm_revision_reference


class HelmRelease(clearskies.Model):
    id_column_name = "name"
    backend = HelmReleaseBackend()

    name = clearskies.columns.String()
    namespace = clearskies.columns.String()
    context = clearskies.columns.String()
    values = clearskies.columns.Json()
    chart_url = clearskies.columns.String()
    chart_name = clearskies.columns.String()
    revisions = clearskies.columns.HasMany(
        helm_revision_reference.HelmRevisionReference,
        foreign_column_name="release_name",
        where=lambda model, parent: model.where(f"namespace={parent.namespace}"),
    )
