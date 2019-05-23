class Context:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy):
        self._strategy = strategy

    def context_segemnt(self, img_path, predictor):
        return self._strategy.segment(img_path, predictor)
