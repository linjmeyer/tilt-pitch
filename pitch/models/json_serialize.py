import jsonpickle

class JsonSerialize:
    def json(self):
        return jsonpickle.encode(self, unpicklable=False)