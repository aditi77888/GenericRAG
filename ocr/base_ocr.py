from abc import ABC, abstractmethod


class BaseOCR(ABC):

    @abstractmethod
    def extract(self, source):
        """
        Performs OCR on the given source.

        Parameters
        ----------
        source : Path

        Returns
        -------
        OCRResponse
        """
        pass