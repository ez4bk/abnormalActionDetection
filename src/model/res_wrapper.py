from src.model.inference_res import InferenceRes
from lib.yolo_detection.inference import Inference


class ResWrapper(object):
    def __init__(self, results=None):
        if results is None:
            results = {}
        self.results = results
        self.res_img_arr = None

    def add_result(self, name: str, conf: float):
        if self.results.get(name):
            self.results[name].add_count()
            self.results[name].append_conf(conf)
            self.results[name].avg_conf()
        else:
            name_res = InferenceRes(name)
            name_res.append_conf(conf)
            self.results[name] = name_res
        return True

    def delete_result(self, name):
        return self.results.pop(name)

    def start_inference(self, img, target=None):
        inference = Inference()
        inference.infer(img)
        # inference.show()
        res = inference.get_res()
        self.res_img_arr = inference.get_img_array()
        for _ in res:
            self.add_result(_[0], _[1])
            if target and _[0] == target:
                return False
        return True

    def get_result(self, name):
        return self.results.get(name)

    def get_res_img_arr(self):
        return self.res_img_arr

    def results_to_list(self):
        res = []
        for _ in self.results.values():
            res.append(_.to_list())
        return res

    def export_to_file(self, file_path):
        with open(file_path, 'w') as f:
            for _ in self.results:
                f.write(str(self.results[_].__str__()) + '\n')

    @staticmethod
    def get_all_cats():
        return Inference().get_all_cats()

    def __str__(self):
        for _ in self.results:
            print(str(self.results[_].__str__()) + '\n')
