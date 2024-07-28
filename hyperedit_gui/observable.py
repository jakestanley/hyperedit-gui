from abc import ABC, abstractmethod

class Observable(ABC):
    def __init__(self) -> None:
        self._observers = []

    def AddObserver(self, observer):
        self._observers.append(observer)

    def NotifyObservers(self):
        for observer in self._observers:
            self.NotifyObserver(observer)

    @abstractmethod
    def NotifyObserver(self, observer):
        raise Exception("NotifyObserver not implemented. Should call relevant `onX` on `observer`")
