import os
import urllib.parse


class ImageUtils:
    @staticmethod
    def add_extension_if_none(file_name: str, extension: str) -> str:
        """Add an extension to a file_name if it has no extension."""
        if not os.path.splitext(file_name)[1]:
            return f'{file_name}.{extension}'
        return file_name

    @staticmethod
    def extract_image_url_from_url(url: str) -> str:
        """Parse image URL from a given HTTP URL."""
        parsed_image_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_image_url.query)
        encoded_url = query_params.get('url', [None])[0]
        return urllib.parse.unquote(encoded_url) if encoded_url else None

    @staticmethod
    def save_file_to_path(file_path: str, file_content: bytes, file_name: str):
        os.makedirs(file_path, exist_ok=True)
        file_path = os.path.join(file_path, file_name)
        with open(file_path, 'wb') as image_file:
            image_file.write(file_content)
