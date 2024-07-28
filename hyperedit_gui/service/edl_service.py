_SINGLETON = None

class EDLService:
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("EDLService MUST not be instantiated more than once")
        pass

    def CreateEDL(self):
        pass

def GetEDLService() -> EDLService:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = EDLService()
    return _SINGLETON
