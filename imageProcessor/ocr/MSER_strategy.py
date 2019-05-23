import os

from ocr.MSERWrapper import MSER_Segmentation
from ocr.strategy import SegmentationStrategy

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]


class MSER_Strategy(SegmentationStrategy):
    """
    Implement the algorithm using the SegmentationStrategy interface.
    """

    def segment(self, img_path, predictor):
        mesr = MSER_Segmentation(img_path, predictor=predictor)
        return mesr.get_lp()
