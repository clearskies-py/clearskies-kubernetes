from clearskies.model import ModelClassReference

from . import helm_release


class HelmReleaseReference(ModelClassReference):
    def get_model_class(self):
        return helm_release.HelmRelease
