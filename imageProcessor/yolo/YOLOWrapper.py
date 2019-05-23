import os

from skimage import io

from yolo.darknet import performDetect

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]


class YOLOWrapper:
    def __init__(self):
        # default paths initialization
        self.__config_path = ROOT_DIR + "/yolo/cfg/yolo-obj3.cfg"
        self.__weight_path = ROOT_DIR + "/yolo/6k_Cluster_3OBJ_04.weights"
        self.__meta_path = ROOT_DIR + "/yolo/cfg/obj3.data"

    def perform_detection(self, image_path="/yolo/data/img45010.jpeg", show_images=False, debug=False):

        if debug:
            print("performing detection on:" + str(image_path))
        image_path = ROOT_DIR + image_path
        detection = performDetect(imagePath=image_path, thresh=0.25,
                                  configPath=self.__config_path,
                                  weightPath=self.__weight_path,
                                  metaPath=self.__meta_path,
                                  showImage=False, makeImageOnly=False, initOnly=False)

        detections_l = []
        objs = []
        for i in range(len(detection)):
            d = detection[i]
            bounds = d[2]
            image = io.imread(image_path)
            shape = image.shape
            # x = shape[1]
            # xExtent = int(x * bounds[2] / 100)
            # y = shape[0]
            # yExtent = int(y * bounds[3] / 100)
            yExtent = int(bounds[3])
            xEntent = int(bounds[2])
            # Coordinates are around the center
            xCoord = int(bounds[0] - bounds[2] / 2)
            yCoord = int(bounds[1] - bounds[3] / 2)

            import cv2
            crop_img = image[yCoord:yCoord + yExtent, xCoord:xCoord + xEntent]
            if show_images:
                cv2.imshow("original", image)
                cv2.imshow("cropped", crop_img)
                cv2.waitKey()
            detections_l.append((d[0], d[1], crop_img))

            objs.append(
                {"x": xCoord, "y": yCoord, "width": xEntent, "height": yExtent, "class": d[0], "precision": d[1],"img":crop_img})

        cars_and_plates = []
        for i in range(len(objs)):
            for j in range(len(objs)):
                if i == j:
                    continue

                if objs[i]["class"] == 'plate' and objs[j]["class"] is not 'plate':
                    if debug:
                        print("found a plate")
                    if objs[i]["x"] > objs[j]["x"] and objs[i]["y"] > objs[j]["y"]:
                        if debug:
                            print("found a plate withing a car")
                        if objs[i]["x"] + objs[i]["width"] < objs[j]["x"] + objs[j]["width"] \
                                and objs[i]["y"] + objs[i]["height"] < objs[j]["y"] + objs[j]["height"]:
                            if debug:
                                print("found a plate withing a car that is not getting outside the car")
                            cars_and_plates.append({"car": objs[j]["img"], "plate": objs[i]["img"]})
        if debug:
            print(objs)
            print("Done detection on image" + str(image_path) + ". Found " + str(len(detections_l)) + " boxes " + " and " + str(len(cars_and_plates)) + " cars with plates associated ")
        return cars_and_plates

    def add_config_path(self, config_path):
        self.__config_path = ROOT_DIR + config_path
        return self

    def add_weight_path(self, weight_path):
        self.__weight_path = ROOT_DIR + weight_path
        return self

    def add_meta_path(self, meta_path):
        self.__meta_path = ROOT_DIR + meta_path
        return self

    def build(self):
        # init the yolo detector, initOnly is set to True, the image is not used so it can be anything
        performDetect(imagePath=ROOT_DIR + "/yolo/data/img45010.jpeg", thresh=0.25,
                      configPath=self.__config_path,
                      weightPath=self.__weight_path,
                      metaPath=self.__meta_path,
                      showImage=True, makeImageOnly=False, initOnly=True)
        return self
