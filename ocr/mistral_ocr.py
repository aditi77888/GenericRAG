import os
import time
from pathlib import Path
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from mistralai.client import Mistral
from mistralai.client.models.file import File

from models.ocr_response import OCRResponse
from ocr.base_ocr import BaseOCR


class MistralOCR(BaseOCR):

    def __init__(self):

        load_dotenv()

        self.client = Mistral(
            api_key=os.getenv("MISTRAL_API_KEY")
        )

    def extract(
            self,
            source,
            output_format="markdown",
            max_retries=3
    ):

        source = Path(source)

        start_time = time.perf_counter()

        last_error = None

        for attempt in range(1, max_retries + 1):

            try:

                uploaded_file = self._upload_file(source)

                return self._process_ocr(
                    uploaded_file.id,
                    output_format,
                    start_time
                )

            except Exception as e:

                last_error = e

                print(
                    f"[MISTRAL OCR] Attempt {attempt}/"
                    f"{max_retries} failed: {e}",
                    flush=True
                )

                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # 2s, 4s, 8s

        raise RuntimeError(
            f"Mistral OCR failed after {max_retries} "
            f"attempts : {last_error}"
        ) from last_error

    def extract_image(
            self,
            image,
            output_format="markdown"
    ):

        start_time = time.perf_counter()

        try:

            uploaded_file = self._upload_image(image)

            return self._process_ocr(
                uploaded_file.id,
                output_format,
                start_time
            )

        except Exception as e:

            raise RuntimeError(
                f"Mistral OCR failed : {e}"
            ) from e
    def _content_type(self, path):

        extension = path.suffix.lower()

        mapping = {

            ".png": "image/png",

            ".jpg": "image/jpeg",

            ".jpeg": "image/jpeg",

            ".pdf": "application/pdf",

            ".webp": "image/webp",

            ".bmp": "image/bmp",

            ".tiff": "image/tiff"

        }

        return mapping.get(

            extension,

            "application/octet-stream"

        )

    def _upload_file(self, source):

        with open(source, "rb") as file:
            return self.client.files.upload(

                file=File(

                    fileName=source.name,

                    content=file,

                    content_type=self._content_type(source)

                ),

                purpose="ocr"

            )

    def _upload_image(self, image):

        if not isinstance(image, Image.Image):
            raise TypeError(
                "extract_image() expects a PIL Image."
            )

        buffer = BytesIO()

        image.save(
            buffer,
            format="PNG"
        )

        image_bytes = buffer.getvalue()

        return self.client.files.upload(

            file=File(

                fileName="page.png",

                content=image_bytes,

                content_type="image/png"

            ),

            purpose="ocr"
        )

    def _process_ocr(
            self,
            file_id,
            output_format,
            start_time
    ):

        signed_url = self.client.files.get_signed_url(

            file_id=file_id

        )

        ocr_response = self.client.ocr.process(

            model="mistral-ocr-latest",

            document={

                "type": "document_url",

                "document_url": signed_url.url

            }

        )

        if output_format == "markdown":

            text = "\n\n".join(

                page.markdown

                for page in ocr_response.pages

            )

        elif output_format == "blocks":

            blocks = []

            for page in ocr_response.pages:

                for block in page.blocks:
                    blocks.append(block.content)

            text = "\n".join(blocks)

        else:

            raise ValueError(
                f"Unknown output format: {output_format}"
            )

        metadata = {

            "engine": "mistral",

            "model": ocr_response.model,

            "pages": ocr_response.usage_info.pages_processed,

            "ocr_time": round(
                time.perf_counter() - start_time,
                3
            )

        }

        return OCRResponse(

            text=text.strip(),

            confidence=None,

            metadata=metadata

        )