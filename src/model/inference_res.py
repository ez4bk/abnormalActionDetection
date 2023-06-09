class InferenceRes(object):
    def __init__(self, name, count=1):
        self.name = name
        self.count = count
        self.confidence = []
        self.avg_confidence = 0

    def add_count(self):
        self.count += 1

    def append_conf(self, conf):
        self.confidence.append(conf)
        self.avg_conf()

    def avg_conf(self):
        self.avg_confidence = round(sum(self.confidence) / len(self.confidence), 2) * 100

    def to_list(self):
        return [self.name, self.count, self.avg_confidence]

    def __str__(self):
        return f"{self.name}: {self.count} with avg confidence of {self.avg_confidence}: {self.confidence}"
