from pathlib import Path

from loaders.base_loader import BaseLoader


class ImageLoader(BaseLoader):

    SUPPORTED_EXTENSIONS = {

        ".png",

        ".jpg",

        ".jpeg",

        ".bmp",

        ".tiff",

        ".webp"

    }

    def load(self, source):

        return self._validate_image(source)

    def _validate_image(self, source):

        path = Path(source)

        if not path.exists():

            raise FileNotFoundError(

                f"Image not found: {path}"

            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:

            raise ValueError(

                f"Unsupported image format: {path.suffix}"

            )

        return path