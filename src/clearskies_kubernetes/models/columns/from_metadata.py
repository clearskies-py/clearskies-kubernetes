from typing import Any, Self, overload

import clearskies


class FromMetadata(clearskies.Column):
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

        # In a test context the data will already be in the raw data, so use it if found
        raw_data = instance.get_raw_data()
        if self.name in raw_data:
            return raw_data[self.name]

        # this only works if the column name matches the name of the key in the metadata object
        return getattr(instance.chart_metadata, self.name)
