from clearskies.model import ModelClassReference

from . import helm_revision


class HelmRevisionReference(ModelClassReference):
    def get_model_class(self):
        return helm_revision.HelmRevision
