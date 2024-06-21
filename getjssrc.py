from bs4 import BeautifulSoup
import requests
import sys
from pprint import pprint
import hashlib
import os


def extract_js_urls(html_content, output_dir):
    soup = BeautifulSoup(html_content, "html.parser")
    js_urls = []

    # Find all script tags
    for script in soup.find_all("script"):
        # Check if the script tag has a 'src' attribute
        if script.get("src"):
            js_urls.append(script["src"])

        # generate a hash from the content of the script tag
        hash = hashlib.md5(script.text.encode()).hexdigest()
        filename = hash + ".js"

        # create a file and write the content of the script tag to the file
        with open(os.path.join(output_dir, filename), "w") as f:
            f.write(script.text)

    return js_urls


# retrieve the content of a URL
def retrieve_url_content(url):

    response = requests.get(url)
    return response.text


def process_js_urls(js_urls, url):
    if url.endswith("/"):
        url = url[:-1]

    js_urls_processed = []
    for js_url in js_urls:
        if js_url.startswith("http"):
            js_urls_processed.append(js_url)
        elif js_url.startswith("//"):
            js_urls_processed.append("https:" + js_url)
        else:
            js_urls_processed.append(url + js_url)
    return js_urls_processed


def download_js_files(js_urls, output_dir):
    for js_url in js_urls:

        # Download the file
        content = requests.get(js_url).content

        # generate a hash from the content of the script tag
        hash = hashlib.md5(content).hexdigest()
        filename = hash + ".js"

        # Download the file
        with open(os.path.join(output_dir, filename), "wb") as f:
            f.write(content)


# cli usage
# python getjssrc.py url
if len(sys.argv) != 3:
    print("Usage: python getjssrc.py <url> <output_dir>")
    sys.exit(1)

url = sys.argv[1]
output_dir = sys.argv[2]

html_content = retrieve_url_content(url)
js_urls = extract_js_urls(html_content, output_dir)
js_urls_processed = process_js_urls(js_urls, url)
download_js_files(js_urls_processed, output_dir)

# for js_url in js_urls_processed:
#     print(js_url)
# pprint(js_urls_processed)
