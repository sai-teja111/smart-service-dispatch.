
class ResultMock:
    def __init__(self, result=None):
        self.result = result

    def first(self):
        return self.result

    def all(self):
        if self.result is None:
            return []

        return self.result


class SessionMock:
    def __init__(
        self,
        result=None,
        results=None,
        get_result=None,
    ):
        self.result = result
        self.results = results
        self.get_result = get_result
        self.exec_count = 0

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return None

    def add(self, obj):
        return None

    def flush(self):
        # Simulate the Session.flush() method for unit tests.
        # This mock does not persist objects or generate database IDs.
        return None

    def commit(self):
        return None

    def refresh(self, obj):
        return None

    def get(self, model, identifier):
        return self.get_result

    def exec(self, query):
        if self.results is not None:
            result = self.results[self.exec_count]
            self.exec_count += 1
            return ResultMock(result)

        return ResultMock(self.result)
