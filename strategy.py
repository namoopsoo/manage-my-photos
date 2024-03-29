import argparse
import os
import json
import re
import requests
import shlex
import subprocess
from imagededup.methods import PHash
from functools import reduce
from glob import glob
from pathlib import Path
from collections import defaultdict
from PIL import Image
from uuid import uuid4
from datetime import datetime
from tqdm import tqdm
import logging
import pytz

import fdups

logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)

c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)

# Add handlers to the logger
logger.addHandler(c_handler)

def utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

def utc_ts(dt):
    return dt.strftime("%Y-%m-%dT%H%M%SZ")


def bake_options():
    return [
            [['--verbose', '-v'],
                {'action': 'store_true',  # stores boolean
                    'help': 'pass to to be verbose with commands'},
                ],
            [['--debug', '-d'],
                {'action': 'store_true',  # stores boolean
                    'help': 'start with ipdb trace'},
                ],
            [['--dry-run', '-D'],
                {'action': 'store_true',
                    'help': 'Dry run. Just print the command.',
                 },],
    

            [['--main-photo-dir', '-m'],
                {'action': 'store',
                    'help': 'Home dir for photos'},],
            [['--photo-dirs', '-p'],
                {'action': 'store',
                    'help': 'Which dirs to dedupe, specified relative to main photo dir'},],
            [['--color', '-c'],
                {'action': 'store',  # Stores the value given
                    'help': 'Dry run. Just print the command.  '},
            ],
            [['--dir-for-review', '-r'],
                {'action': 'store',
                    'help': 'Use this dir for dumping .png files, which are probably screenshots I don\'t want in my photo collection.'},],


            [['--action', '-a'],
                {'action': 'store',
                    'help': 'choose between deduping, or move phood photos, say',
                    'choices': ["move-pngs", "dedupe", "move-food", "all"],
                 },],

            [['--food-dir', '-F'],
                {'action': 'store',
                    'help': 'what dir to move food to '},],

                ]


def get_file_size(path):
    return path.stat().st_size
    # return round(path.stat().st_size / 1024 / 1024, 1)
  

def dedupe_folder(phasher, folder):
    # Assert files exist and sizes are at least 1 meg.   
    extensions = ["jpg", "JPG", "jpeg", "JPEG"]
    files = reduce(lambda x, y: x + y,
        [glob(str(Path(folder)/ f"*.{extension}")) for extension in extensions])
    sizes = [[x, get_file_size(Path(x))] for x in files]
    smallest = sorted(sizes, key=lambda x: x[1])[0]
    if smallest[1] == 0:
        print(smallest)
        logger.error(f"folder {folder} has 0Byte files, so not ready yet.")
        return
    
    out_vec = []
    ... 
    encodings = phasher.encode_images(image_dir=folder)
    clashes = defaultdict(list)
    len([clashes[v].append(k) for (k, v) in encodings.items()])

    for k, v in clashes.items():
        if len(v) > 1:
            delete_these, keep = which_delete(v)
            if delete_these and all(
                    [(Path(folder) / x).is_file() for x in delete_these]):
                for x in delete_these:
                    os.remove(Path(folder) / x)
                out_vec.append({"outcome": "deduped",
                               "deleted": delete_these, "kept": keep})
            else:
                out_vec.append({"outcome": "didnt_dedupe", 
                               "files": v, "encoding": k,})
    return out_vec
  
def which_delete(v):
    """Pick which filename to delete among a list of duplicate files.

    Prefer filenames that match a date regex.
    """
    date_re = r"\d{4}-\d{2}-\d{2}"
    dated = [x for x in v if re.match(date_re, x)]
    if dated:
        delete_these = list(set(v) - set([dated[0]]))
        return delete_these, dated[0]
    else:
        first_one = v[0]
        delete_these = list(set(v) - set([v[0]]))
        return delete_these, v[0]
       
def dedupe_action(main_photo_dir, photo_dirs):
    phasher = PHash()
    all_vec = []
    workdir = Path(main_photo_dir)
    for folder in photo_dirs:
        assert (workdir / folder).is_dir()
        out_vec = dedupe_folder(phasher, str(workdir / folder))
        all_vec.extend(out_vec)
        if out_vec:
            deleted_count = sum([len(x["deleted"]) for x in out_vec if "deleted" in x])
            kept_count = sum([1 for x in out_vec if "kept" in x])
            logger.info(f"folder {folder} {deleted_count} deleted, {kept_count} kept.")
            print(f"folder {folder} {deleted_count} deleted, {kept_count} kept.")
        ...

    logger.info("done")
    return all_vec

    
def move_pngs(main_photo_dir, photo_dirs, dir_for_review):
    to_delete = []
    renamed = []
    moved = []
    for folder in photo_dirs:
        for suffix in ["PNG", "png"]:
            for file in (main_photo_dir / folder).glob(f"*.{suffix}"):
                new_path = dir_for_review / folder / file.name
                new_path.parent.mkdir(parents=True, exist_ok=True)
                if new_path.exists():
                    hash1 = fdups.get_file_hash(file)
                    hash2 = fdups.get_file_hash(new_path)
                    if hash1 == hash2:
                        # Delete the first then, 
                        to_delete.append(str(file))
                    else:
                        # Rename first. 
                        new_path = dir_for_review / folder / (file.stem + f"-{str(uuid4())[:8]}{file.suffix}")

                        # Make any parent dirs
                        new_path.parent.mkdir(parents=True, exist_ok=True)

                        file.replace(new_path)
                        moved.append([str(file), str(new_path)])
                else:
                    file.replace(new_path)
                    moved.append([str(file), str(new_path)])

    loc = main_photo_dir / f"move-log-{utc_ts(utc_now())}.json"
    loc.write_text(json.dumps({"to_delete": to_delete, "moved": moved}))

    for file in to_delete:
        os.remove(file)


def invoke_one_image(image_absolute_path, base_dir):
    image_file = image_absolute_path.name
    assert image_absolute_path.exists()

    out = requests.post("http://0.0.0.0:8080/invocations", 
        json=[str(image_absolute_path.relative_to(base_dir))])

    if out.status_code != 200:
        print(out.status_code, out.text)
    result = out.json()["result"][0]
    return result["prediction"], result["raw"]


def move_food(main_photo_dir, photo_dirs, food_dir):

    assert main_photo_dir.is_dir()
    assert food_dir.is_dir()
    out_vec = []
    for folder in photo_dirs:
        source_dir = (main_photo_dir / folder)
        assert source_dir.is_dir()

        extensions = ["jpg", "JPG", "jpeg", "JPEG"]
        files = reduce(lambda x, y: x + y,
            [glob(str(source_dir / f"*.{extension}")) for extension in extensions])

        for image_path in tqdm(files):
            image_path = Path(image_path)
            out = invoke_one_image(image_path, main_photo_dir)
            print(image_path.name, out)
            (prediction, pred_logits_str) = out
            info = {"image": str(image_path), "pred": out}
            if prediction == "food":
                new_path = food_dir / folder / image_path.name

                # Make parent dirs.
                new_path.parent.mkdir(parents=True, exist_ok=True)

                if new_path.exists():
                    print("weird,", new_path, "already exists, not replacing..")
                    info["action"] = "already_existed_no_action"
                else:
                    image_path.replace(new_path)
                    info["action"] = "moved"
            else:
                ...
                ...
            out_vec.append(info)
        ...
    out_vec
    loc = main_photo_dir / f"move-log-{utc_ts(utc_now())}.json"
    loc.write_text(json.dumps({"out_vec": out_vec}))
    ...
    

def ping_server():
    out = requests.get("http://0.0.0.0:8080/ping")
    if out.status_code != 200:
        print(out.status_code, out.text)
        return False
    return True

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    [parser.add_argument(*x[0], **x[1]) for x in bake_options()]

    args = dict(vars(parser.parse_args()))
    print("args", args)
    if args.get("debug"):
        import ipdb; ipdb.set_trace()

    main_photo_dir = Path(args["main_photo_dir"])
    assert main_photo_dir.is_dir()

    photo_dirs = args.get("photo_dirs")
    if photo_dirs:
        photo_dirs = photo_dirs.split(",")
        for folder in photo_dirs:
            assert (main_photo_dir / folder).is_dir()

    import ipdb; ipdb.set_trace()

    if not ping_server():
        raise Exception("Server health check failed")


    all_actions = ["move-pngs", "dedupe", "move-food"]
    if args.get("action") == "all":
        actions = all_actions
    elif args.get("action") in all_actions:
        actions = [args.get("action")]

    for action in actions:
        if action == "dedupe":
            all_vec = dedupe_action(main_photo_dir, photo_dirs)
        elif action == "move-pngs":
            dir_for_review = Path(args.get("dir_for_review"))
            move_pngs(main_photo_dir, photo_dirs, dir_for_review)

        elif action == "move-food":
            food_dir = Path(args["food_dir"])
            move_food(main_photo_dir, photo_dirs, food_dir)
        else:
            raise Exception("unknown action")


