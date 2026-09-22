import clearskies
from pyhelm3 import models as helm_models

from clearskies_kubernetes.backends import HelmRevisionBackend

from . import helm_release_reference
from .columns.from_helm_method import FromHelmMethod
from .columns.from_metadata import FromMetadata


class HelmRevision(clearskies.Model):
    id_column_name = "name"
    backend = HelmRevisionBackend()

    revision_number = clearskies.columns.Integer()
    release_name = clearskies.columns.BelongsToId(
        helm_release_reference.HelmReleaseReference,
    )
    namespace = clearskies.columns.String()
    context = clearskies.columns.String()
    is_latest = clearskies.columns.Boolean()
    status = clearskies.columns.Select([status.value for status in helm_models.ReleaseRevisionStatus])
    updated = clearskies.columns.Datetime()
    description = clearskies.columns.String()
    notes = clearskies.columns.String()
    chart_metadata = FromHelmMethod()
    hooks = FromHelmMethod()
    resources = FromHelmMethod()
    values = FromHelmMethod()
    app_version = FromMetadata()

    release = clearskies.columns.BelongsToModel("release_name")
