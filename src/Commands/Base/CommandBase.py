from abc import ABC, abstractmethod


class CommandBase(ABC):
    @property
    @abstractmethod
    def command_name(self):
        pass

    @property
    @abstractmethod
    def command_description(self):
        pass

    @abstractmethod
    def get_command_instance(self):
        pass
