import os
import pathlib
import re
from collections import Counter
from tqdm import tqdm

import s3


def relative(path, rebase=None, index=None):
    if rebase:
        index = path.parts.index(rebase)
        return pathlib.Path("/".join(path.parts[index:]))
    else:
        return pathlib.Path("/".join(path.parts[index:]))
    


def main(local_base_dir, photo_dir_name, bucket):
    source_dir = pathlib.Path(local_base_dir) / photo_dir_name
    assert source_dir.exists()

    p = source_dir.glob("**/*")
    have_files = [x for x in p if x.is_file()]

    haves_relative = [str(relative(path, rebase=photo_dir_name)) for path in have_files]

    files = s3.listdir(bucket, s3prefix=photo_dir_name, list_all=True) 
    remaining_list = list(set(haves_relative) - set(files))
    transfered_so_far = len(set(haves_relative) & set(files))

    print(remaining_list[:5], "...", remaining_list[-5:])
    print("transfered so far", transfered_so_far)
    print("remaining", len(remaining_list))
    answer = input("go ahead? [y/n]")

    if answer != "y":
        return
    for path in tqdm(remaining_list):
        absolute_local_path = pathlib.Path(local_base_dir) / path
        s3_path = path
        transfer_file(bucket, absolute_local_path, s3_path)


    print("Done")

def transfer_file(bucket, absolute_local_path, s3_path):
    assert absolute_local_path.exists()

    content = absolute_local_path.read_bytes()

    out = s3.write_this(bucket, s3_path, content)
    return out


def new_folders_for_year(base_dir):
    year = base_dir.parts[-1]
    assert re.match(r"^20\d\d$", year)
    dirs = []
    for month in range(1, 13):
        folder = (base_dir / f"{year}-{str(month).zfill(2)}")
        if not folder.exists():
            dirs.append(folder)
            os.mkdir(folder)
    return dirs
    
def move_files(from_dir, to_dir, prefix, filetype, dry_run=False):
    path = from_dir.glob(prefix + "*" + filetype)
    files = sorted(list(path))
    suffixes = Counter([x.suffix for x in files])
    base_months = Counter([x.name[:7] for x in files])
    if len(base_months) != 1:
        print("quitting oops, multiple months, ", base_months)
        return
    base_month = list(dict(base_months).keys())[0]
    year = base_month[:4]
    new_dir = to_dir / year / base_month
    if not new_dir.exists():
        print("Dir doesnt exist", new_dir)
        return

    print(files[0].name, "...", files[-1].name, f"({dict(suffixes)})")
    answer = input(f"Move {len(files)} files? [y/n]")
    if answer != "y":
        return

    move_count = 0
    did_not_overwrite_count = 0
    for file in tqdm(files):
        new_path = new_dir / file.name
        if new_path.exists():
            did_not_overwrite_count += 1
        else:
            if not dry_run:
                file.replace(new_path)
                move_count += 1
    print("Done moving", move_count, f"files, ({did_not_overwrite_count} already existed)")

