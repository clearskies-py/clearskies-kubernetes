from typing import Any, Self, overload

import clearskies


class FromHelmMethod(clearskies.Column):
    def __init__(self):
        self.is_readable = True
        self.is_writeable = False

    @overload
    def __get__(self, instance: None, cls: type[clearskies.Model]) -> Self:
        pass

    @overload
    def __get__(self, instance: clearskies.Model, cls: type[clearskies.Model]) -> dict[str, Any]:
        pass

    def __get__(self, instance, cls):
        if instance is None:
            self.model_class = cls
            return self

        raw_data = instance.get_raw_data()
        # This works because only the revision has a revision object, but they both have a release object.
        # This column can work with both models, and I don't bother figuring out which is which, because
        # (per the above) only the release model has a release object.
        helm_object = raw_data.get("revision_object", raw_data.get("release_object"))

        # this only works if the column name matches the name of the metod in the pyhelm3 sdk
        return getattr(helm_object, self.name)()
