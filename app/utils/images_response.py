import json
from typing import List


def get_image_url(match_ids: List[int]) -> List[str]:
    """Get images url from their IDS

    Args:
        match_ids (List[int]) : The images's IDs

    Returns:
        List[str]: The images's url
    """
    with open("./id2url.json", "r") as f:
        id2url = json.load(f)
    images_url = []
    for i in match_ids:
        images_url.append(id2url[i])
    return images_url


def display_html(images_url: List[str]) -> str:
    """Display the html content from images url
    Args:
        match_ids (List[str]) : The images's url

    Returns:
        str : html content
    """

    html_content = """
    <html>
        <head>
            <title>Dynamic Images</title>
            <style>
                .image-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    grid-gap: 10px;
                }
                .image {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <div class="image-grid">
    """

    for url in images_url:
        html_content += f'<img src="{url}" alt="Image" width="200" height="300">'

    html_content += """
            </body>
        </html>
    """
    return html_content
