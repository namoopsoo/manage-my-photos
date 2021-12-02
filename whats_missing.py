import os
import pathlib
import s3
from tqdm import tqdm

#def walk_dir(this_dir):

def relative(path, rebase=None, index=None):
    if rebase:
        index = path.parts.index(rebase)
        return pathlib.Path("/".join(path.parts[index:]))
    else:
        return pathlib.Path("/".join(path.parts[index:]))
    


def main(local_base_dir, photo_dir_name, bucket):
    # bucket = "photos-mmkay"
    # local_base_dir = "/Users/michal/LeDropbox/Dropbox/myphotos"
    # source_dir = "/Users/michal/LeDropbox/Dropbox/myphotos/2009"
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

