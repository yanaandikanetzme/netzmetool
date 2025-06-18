class logger():
    def __init__(self, parent):
        super().__init__(parent)

    def logger():
        logger = {'debug': lambda o: o}
        logger = logger.copy()
        return logger

    def enableDebugLog():
        enableDebugLog = lambda: globals().update({'logger': print})
        return enableDebugLog