from flask import Flask, jsonify, request
import flask
import json
import os
from functools import reduce
from pathlib import Path

from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Set the path to the image folder
IMAGE_FOLDER = "/Users/michal/Dropbox/myphotos"
IMAGE_FOLDER = "/Users/michal/Dropbox/myphotos/2019/2019-04"

# Set the path to the destination folder
DESTINATION_FOLDER = "/Users/michal/Dropbox/myphotos/not-for-icloud-photos" 
DESTINATION_FOLDER = "/Users/michal/Dropbox/myphotos/not-for-icloud-photos/2019/2019-04"
# /Users/michal/Dropbox/FoodJournal/2019/2019-04

FOR_LOGSEQ_FOLDER = "/Users/michal/Dropbox/myphotos/for-logseq/2019/2019-04"

FOOD_JOURNAL = "/Users/michal/Dropbox/FoodJournal"

# Get the list of image files
image_files = Path(IMAGE_FOLDER).glob("*.jpg")


extensions = ["jpg", "JPG", "jpeg", "JPEG"]
image_files = reduce(lambda x, y: x + y,
    [glob(str(IMAGE_FOLDER / f"*.{extension}")) for extension in extensions])

# Initialize the current index
current_index = 0


@app.route("/", methods=["GET"])
def get_image():
    global current_index

    # Check if we have reached the end of the list
    if current_index == len(image_files):
        return jsonify({"message": "No more images to display"})

    # Get the filename of the current image
    filename = image_files[current_index]

    # Increment the index for the next request
    current_index += 1

    # Return the filename as JSON
    # return jsonify()
    payload = {"filename": filename}

    return make_response(payload)


def make_response(data):
    str_payload = json.dumps(data)

    mimetype = "application/json"
    response = flask.Response(response=str_payload,
                              status=200,
                              mimetype=mimetype)
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # CORS_ORIGIN_ALLOW_ALL = True?
    # response.headers["Content-Type"] = "application/json"

    return response

@app.route("/", methods=["POST"])
def move_image():
    # Get the filename and choice from the request data
    filename = request.json.get("filename")
    choice = request.json.get("choice")

    # Check if the filename and choice are valid
    if not filename or not choice:
        payload = {"message": "Invalid request data"}
        return make_response(payload)
    # return jsonify(payload)

    import ipdb; ipdb.set_trace()

    # Check if the source file exists
    src_path = Path(IMAGE_FOLDER) / filename
    if not src_path.exists():
        return jsonify({"message": "File not found"})

    if choice == "photo-library":
        return jsonify({"message": "File kept!"})

    if choice == "trash":
        os.remove(str(src_path))
        return jsonify({"message": f"{src_path} trashed."})

    if choice == "for-logseq":

    # Set destination path
    dest_path = Path(DESTINATION_FOLDER) / choice / filename

    # Create the destination directory if it does not exist
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Move the file to the destination directory
    os.rename(src_path, dest_path)

    # Return a success message
    return jsonify({"message": "File moved successfully"})


if __name__ == "__main__":
    app.run(debug=True)

