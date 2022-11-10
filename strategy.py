import argparse
import os
import json
import re
from imagededup.methods import PHash
from pathlib import Path
from collections import defaultdict
from PIL import Image
from uuid import uuid4

import fdups

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
                    'help': 'Dry run. Just print the command.'},],

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


                ]


def get_file_size(path):
    return round(path.stat().st_size / 1024 / 1024, 1)
  

def dedupe_folder(phasher, folder):
    # TODO might assert files exist and sizes are at least 1 meg.   
    out_vec = []
    encodings = phasher.encode_images(image_dir=folder)
    clashes = defaultdict(list)
    len([clashes[v].append(k) for (k, v) in encodings.items()])

    for k, v in clashes.items():
        if len(v) > 1:
            delete_these, keep = which_delete(v)
            if delete_these and all(
                    [(folder / x).is_file() for x in delete_these]):
                for x in delete_these:
                    os.remove(folder / x)
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
       
def main(main_photo_dir):
    phasher = PHash()
    all_vec = []
    workdir = Path(main_photo_dir)
    for folder in ["2021-01", "2021-02", "2021-03", 
                   "2021-04", "2021-05", "2021-06"
                  ]:
        assert (workdir / folder).is_dir()
        out_vec = dedupe_folder(phasher, workdir / folder)
        all_vec.extend(out_vec)
    return all_vec

    
def move_pngs(main_photo_dir, photo_dirs, dir_for_review):
    to_delete = []
    renamed = []
    moved = []
    for folder in photo_dirs:
        for suffix in ["PNG", "png"]:
            for file in (main_photo_dir / folder).glob(f"*.{suffix}"):
                new_path = dir_for_review / file.name
                if new_path.exists():
                    hash1 = fdups.get_file_hash(file)
                    hash2 = fdups.get_file_hash(new_path)
                    if hash1 == hash2:
                        # delete the first then, 
                        to_delete.append(str(file))
                    else:
                        # rename first. 
                        new_path = dir_for_review / (file.stem + f"-{str(uuid4())[:8]}{file.suffix}")
                        # renamed.append([file.name, new_path.name])
                file.replace(new_path)
                moved.append([file.name, new_path.name])
                ...

            ...
        ...
    ...
        
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    [parser.add_argument(*x[0], **x[1]) for x in bake_options()]

    args = dict(vars(parser.parse_args()))
    if args.get("debug"):
        import ipdb; ipdb.set_trace()

    main_photo_dir = Path(args["main_photo_dir"])
    assert main_photo_dir.is_dir()

    photo_dirs = args.get("photo_dirs")
    if photo_dirs:
        photo_dirs = photo_dirs.split(",")
        for folder in photo_dirs:
            assert (main_photo_dir / folder).is_dir()

    print("args", args)
    if dir_for_review := Path(args.get("dir_for_review")):
        move_pngs(main_photo_dir, photo_dirs, dir_for_review)

    #all_vec = main()
