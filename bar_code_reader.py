from pdf2image import convert_from_path, convert_from_bytes
import numpy as np
import cv2
from PIL import Image
from pyzbar import pyzbar


class ReadBarCodes:
    """Read data from two bar codes on pdf."""
    def __init__(self, pdf_path: str):
        self.long_bar_code_dimensions = {'top': 45, 'bottom': 112, 'left': 5, 'right': 760}
        self.tagged_by_dimensions = {'top': 420, 'bottom': 520, 'left': 40, 'right': 250}
        self.pdf_path = pdf_path

    def _create_bar_codes(self):
        """Create jpgs containing bar codes only"""
        self._create_bar_code_jpg(self.long_bar_code_dimensions, 'long-bar-code')
        self._create_bar_code_jpg(self.tagged_by_dimensions, 'tagged-by')

    def get_data_from_bar_codes(self) -> dict:
        """Read data from bar codes and return them in a dict."""
        self._create_bar_codes()

        long_bar_code_value = self._read_bar_code('long-bar-code.jpg')
        tagged_by_value = self._read_bar_code('tagged-by.jpg')

        return {'long barcode': long_bar_code_value, 'TAGGED BY': tagged_by_value}

    def _convert_pdf_to_jpg(self) -> list:
        """Convert pdf to jpg for magic to work."""
        images = convert_from_path(self.pdf_path)

        # convert PIL images to cv2
        images = [np.array(i)[:, :, ::-1] for i in images]

        return images

    def _create_bar_code_jpg(self, dimensions_dict: dict, file_name: str) -> None:
        """Remove all other elements from jpg leaving only bar code."""
        images = self._convert_pdf_to_jpg()

        for nr, image in enumerate(images):

            image_to_save = image[
                    dimensions_dict['top']:dimensions_dict['bottom'],
                    dimensions_dict['left']:dimensions_dict['right']
                    ]

            # save cropped image
            cv2.imwrite(f"{file_name}.jpg", image_to_save)

    @staticmethod
    def _read_bar_code(image_name: str) -> any:
        """Read bar code data from jpg."""

        # load image
        bar_code_image = Image.open(image_name)

        # decode bar code
        barcodes = pyzbar.decode(bar_code_image)

        # get bar code data
        return barcodes[0].data.decode('utf-8')
