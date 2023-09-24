import argparse
import webbrowser

import requests

base_api = f"http://retrieval.com"


class DisplayImage:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(description="arguments")
        parser.add_argument(
            "--save_dir", type=str, help="html file to display", required=True
        )

        query_group = parser.add_mutually_exclusive_group()
        query_group.add_argument("--text_query", type=str, help="text query")
        query_group.add_argument("--image_query", type=str, help="image file query")

        args = parser.parse_args()
        print(args)
        self.save_dir = args.save_dir
        self.image_query = args.image_query
        self.text_query = args.text_query

    def request_text(self, text_query):
        text_api = f"{base_api}/display_text"

        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }

        params = {"text_query": text_query}

        response = requests.post(text_api, params=params, headers=headers)
        if response.status_code == 200:
            self._display(response)

    def request_image(self, image_file):
        image_api = f"{base_api}/display_image"
        image = open(image_file, "rb")
        files = {"image_file": image}

        response = requests.post(image_api, files=files)
        if response.status_code == 200:
            self._display(response)

    @staticmethod
    def _display(response):
        with open("temp.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            webbrowser.open("temp.html")

    def main(self):
        if self.text_query is not None:
            self.request_text(self.text_query)
        else:
            self.request_image(self.image_query)


if __name__ == "__main__":
    DisplayImage().main()