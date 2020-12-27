class SingletonMeta(type):
    __instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta.__instance:
            SingletonMeta.__instance[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta.__instance[cls]
