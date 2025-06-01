
import argparse
import json
import os
from pathlib import Path
import requests


from dotenv import load_dotenv

load_dotenv()

def bake_options():
    return [
        [['--trace', '-t'],
            {'action': 'store_true',
                'help': 'trace.'},],

        [['--local-path', '-l'],
            {'action': 'store',
                'help': 'path of file to upload'},],
    ]

def read_kwargs():
    parser = argparse.ArgumentParser()

    [parser.add_argument(*x[0], **x[1])
            for x in bake_options()]

    # Collect args from user.
    kwargs = dict(vars(parser.parse_args()))
    return kwargs

def get_file_size(path):

    file_path = Path(path)
    file_size_bytes = file_path.stat().st_size

    return file_size_bytes

def upload(local_path):

    TOKEN = os.getenv("VIMEO_TOKEN")
    file_size_bytes = get_file_size(local_path)

    # step 1: create an upload uri
    response = requests.post(
        url="https://api.vimeo.com/me/videos",
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.vimeo.*+json;version=3.4",
        },
        json=({"upload": {"approach": "tus", "size": str(file_size_bytes)}})
    )
    print("response", response.json())

    approach = response.json()["upload"]["approach"]
    if approach != "tus":
        print("oops")
        return

    upload_link_url = response.json()["upload"]["upload_link"]

    patch_response = requests.patch(
        url=upload_link_url,
        headers={
            "Content-Type": "application/offset+octet-stream",
            "Tus-Resumable": "1.0.0",
            "Upload-Offset": "0",
        },
        data=Path(local_path).read_bytes(),
    )

    print("patch_response", patch_response)
    print("bye")

if __name__ == "__main__":
    args = read_kwargs()
    if args["trace"]:
        import ipdb; ipdb.set_trace()

    path = args["local_path"]
    upload(path)
    ...