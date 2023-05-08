from flask import Flask, jsonify, request
import re
from glob import glob
import flask
import json
import os
from functools import reduce
from pathlib import Path

from flask_cors import CORS


cache = json.loads(Path("cache.json").read_text())
def update_cache():
    Path("cache.json").write_text(json.dumps(cache))

app = Flask(__name__)
CORS(app)


# Set the path to the image folder
IMAGE_FOLDER = "/Users/michal/Dropbox/myphotos/2019/2019-04"
IMAGE_FOLDER = "/Users/michal/Dropbox/myphotos"

# Set the path to the destination folder
OTHER_FOLDER = "/Users/michal/Dropbox/myphotos/not-for-icloud-photos" 
# /Users/michal/Dropbox/FoodJournal/2019/2019-04

FOR_LOGSEQ_FOLDER = "/Users/michal/Dropbox/myphotos/for-logseq"

# trips 
TRIPS_FOLDER = "/Users/michal/Dropbox/MyTrips"

# things
THINGS_FOLDER = "/Users/michal/Dropbox/ThingsDocuments"
FUNNIES_FOLDER = "/Users/michal/Dropbox/Funnies"
RECEIPTS_FOLDER = "/Users/michal/Dropbox/Receipts"
FOOD_JOURNAL = "/Users/michal/Dropbox/FoodJournal"

# Get the list of image files
# image_files = (Path(IMAGE_FOLDER) / "2019" / "2019-04"
#                ).glob("*.jpg")

extensions = ["jpg", "JPG", "jpeg", "JPEG"]
def next_image(yyyy, mm):
    path = Path(IMAGE_FOLDER) / yyyy / f"{yyyy}-{mm}"
    image_file_paths = reduce(lambda x, y: x + y,
        [glob(str( path / f"*.{extension}")) 
         for extension in extensions])
    image_files = [Path(x).name for x in image_file_paths]

    i = 0 
    if len(image_files) == 0:
        return None, f"no images in {path}."
    images_not_checked = [x for x in image_files
                          if x not in cache]
    if images_not_checked:
        filename = images_not_checked[0]
        return filename, "all good here"
    
    return None, f"all images already processed, (these are in cache, {image_files[:5]})"

@app.route("/", methods=["GET"])
def get_image():

    yyyyMM = request.args.get("yyyyMM")
    match = re.match(r"^(\d\d\d\d)-(\d\d)$", yyyyMM)
    if not match:
        # TODO error return
        return jsonify({"message": f"oops, {yyyyMM} not following yyyy-mm"})
    yyyy, mm = match.groups()[0], match.groups()[1]
    print("yyyy", yyyy, "mm", mm)

    filename, error = next_image(yyyy, mm)
    if not filename:
        # TODO error return
        return jsonify({"message": f"No more images to display , {error}"})

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
    filename = request.json.get("filename").strip("<p>").strip("</p>")
    choice = request.json.get("choice")
    yyyy_mm = request.json.get("yyyymm")
    print("DEBUG", (filename, choice, yyyy_mm))

    # Check if the filename and choice are valid
    if not filename or not choice or not yyyy_mm:
        payload = {"message": "Invalid request data"}
        return make_response(payload)

    match = re.match(r"^(\d\d\d\d)-(\d\d)$", yyyy_mm)
    if not match:
        # TODO error return
        payload = {"message": f"oops, {yyyyMM} not following yyyy-mm"}
        return make_response(payload)

    
    year, month = yyyy_mm.split("-")

    # Check if the source file exists
    src_path = Path(IMAGE_FOLDER) / year / yyyy_mm / filename
    if not src_path.exists():
        return jsonify({"message": "File not found"})  # TODO handle this.

    if choice == "photo-library":

        cache[filename] = 1
        update_cache()
        return jsonify({"message": "File kept!"})

    if choice == "trash":
        os.remove(str(src_path))
        return jsonify({"message": f"{src_path} trashed."})

    if choice == "for-logseq":
        dest_path = Path(FOR_LOGSEQ_FOLDER) / year / yyyy_mm / filename
    elif choice == "things":
        dest_path = Path(THINGS_FOLDER) / year / yyyy_mm / filename
    elif choice == "receipts":
        dest_path = Path(RECEIPTS_FOLDER) / year / yyyy_mm / filename
    elif choice == "trips":
        dest_path = Path(TRIPS_FOLDER) / year / yyyy_mm / filename
    elif choice == "funnies":
        dest_path = Path(FUNNIES_FOLDER) / year / yyyy_mm / filename

    elif choice == "food":
        dest_path = Path(FOOD_JOURNAL) / year / yyyy_mm / filename

    elif choice == "other":
        dest_path = Path(OTHER_FOLDER) / year / yyyy_mm / filename
    else:
        return jsonify({"message": f"choice {choice} unrecognized."})


    # Create the destination directory if it does not exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    # os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Move the file to the destination directory
    # os.rename(src_path, dest_path)
    src_path.replace(dest_path)

    # Return a success message
    return jsonify({"message": f"File {src_path} moved successfully to {dest_path}"})


if __name__ == "__main__":
    app.run(debug=True)

