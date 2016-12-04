class SkytapUser(object):
    _registry = []

    def __init__(self, name, username, password, apikey):
        self.addUserToRegistry()
        self.name = name
        self.username = username
        self.password = password
        self.apikey = apikey
        self.screenshotlist = []

    def addUserToRegistry(self):
        self._registry.append(self)