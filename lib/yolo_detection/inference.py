# from ultralytics import YOLO as yolov5
from PIL import Image
import yolov5

from config import MODEL_DIR, SETTINGS_DATA


class Inference(object):
    def __init__(self, settings=SETTINGS_DATA):
        # load model
        self.model = yolov5.load(MODEL_DIR)
        self.set_param(settings)
        self.results = None
        self.confidence = None
        self.categories = None

    def set_param(self, settings):
        # set model parameters
        self.model.conf = settings['confidence']  # NMS confidence threshold
        self.model.iou = settings['iou']  # NMS IoU threshold
        self.model.agnostic = settings['agnostic']  # NMS class-agnostic
        self.model.multi_label = settings['multi_label']  # NMS multiple labels per box
        self.model.max_det = settings['max_det']  # maximum number of detections per image

    def set_conf(self, confidence):
        self.model.conf = confidence

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

