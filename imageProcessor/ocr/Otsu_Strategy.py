from ocr.OtsuWrapper import Otsu_Segmentation
from ocr.strategy import SegmentationStrategy


class Otsu_Strategy(SegmentationStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def segment(self, img_path, predictor):
        otsu = Otsu_Segmentation(img_path, predictor=predictor)
        return otsu.get_lp()
