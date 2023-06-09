# from ultralytics import YOLO as yolov5
from PIL import Image
from ultralytics import YOLO
import torch.cuda as cuda


class Inference(object):
    def __init__(self, supervised=True):
        # load model

        self.model = YOLO('yolov8n_sup.pt') if supervised else YOLO('yolov8n_unsup.pt')
        params = {
            "conf": 0.7,
            "device": 0 if cuda.is_available() else 'cpu'
        }
        self.results = None
        self.confidence = None
        self.categories = None

    def infer(self, img=None):
        self.results = self.model(img)

        # self.results = self.model(img, size=1280)   # inference with larger input size
        # self.results = self.model(img, augment=True)    # inference with test time augmentation

        # parse results
        predictions = self.results.pred[0]
        # boxes = predictions[:, :4]  # x1, y1, x2, y2
        self.confidence = predictions[:, 4]
        self.categories = predictions[:, 5]

    def show(self):
        # show detection bounding boxes on image
        self.results.show()

    def get_res(self):
        res = []
        for cat, conf in zip(self.categories, self.confidence):
            res.append((self.model.names[int(cat)], round(float(conf), 2)))
        return res

    def get_img(self):
        return Image.fromarray(self.results.render()[0])

    def get_img_array(self):
        return self.results.render()[0]

    def get_all_cats(self):
        return list(self.model.names.values())

