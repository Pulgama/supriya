import abc

import supriya.realtime


class SessionFactory:

    ### INITIALIZER ###

    def __init__(self, input_bus_channel_count=None, output_bus_channel_count=None):
        self._options = supriya.realtime.BootOptions(
            input_bus_channel_count=input_bus_channel_count,
            output_bus_channel_count=output_bus_channel_count,
        )

    ### SPECIAL METHODS ###

    def __render__(self, **kwargs):
        session = self.__session__()
        return session.__render__(**kwargs)

    @abc.abstractmethod
    def __session__(self):
        raise NotImplementedError

    ### PUBLIC METHODS ###

    @classmethod
    def from_project_settings(cls, project_settings):
        import supriya.cli
        import supriya.realtime

        assert isinstance(project_settings, supriya.cli.ProjectSettings)
        server_options = supriya.realtime.BootOptions(
            **project_settings.get("server_options", {})
        )
        input_bus_channel_count = server_options.input_bus_channel_count
        output_bus_channel_count = server_options.output_bus_channel_count
        return cls(
            input_bus_channel_count=input_bus_channel_count,
            output_bus_channel_count=output_bus_channel_count,
        )

    ### PUBLIC PROPERTIES ###

    @property
    def input_bus_channel_count(self):
        return self.options.input_bus_channel_count

    @property
    def options(self):
        return self._options

    @property
    def output_bus_channel_count(self):
        return self.options.output_bus_channel_count
