# http://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them/748908#748908

import sys
import os
import hashlib
import json
import datetime

'''
README: currently this outputs a log into the current working directory.

Usage:

python fdups.py path1 [path2 [path3 [...]]]

TODO: remove empty folders?
'''

def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_file_hash(full_path):
    hashobj = hashlib.sha1()
    try:
        for chunk in chunk_reader(open(full_path, 'rb')):
            hashobj.update(chunk)

        digest = hashobj.hexdigest()
        return digest
    except OSError as e:
        return None


def check_for_duplicates(paths, ignore_extensions=None, explicit_extensions=None):
    hashes = {}
    duplicates_list = []
    oserror_list = []
    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in sorted(filenames):
                extension = filename.split(".")[-1]
                if extension.lower() in ignore_extensions:
                    continue
                if extension.lower() not in explicit_extensions:
                    continue
                full_path = os.path.join(dirpath, filename)
                file_digest = get_file_hash(full_path)
                if not file_digest:
                    oserror_list.append(full_path)
                    continue
                file_size = os.path.getsize(full_path)
                file_tuple = (file_digest, file_size)
                existing_file = hashes.get(file_digest, None)
                if existing_file:
                    existing_file_path = existing_file['path']
                    duplicate_path = full_path
                    print(f"Duplicate found: {existing_file_path} and {duplicate_path} , {file_tuple}")
                    duplicates_list.append(duplicate_path)
                else:
                    if file_size < 10:
                        continue
                    hashes[file_digest] = {'path': full_path, 'size': file_size}
    return duplicates_list, hashes, oserror_list


def remove_files(files_list):
    # delete
    for filepath in set(files_list):
        try:
            os.remove(filepath)
        except OSError:
            import pdb; pdb.set_trace()
            print(f'cannot find {filepath} ')
    print('done removing')


def dump_index(hash_index):
    outfile = datetime.datetime.now().strftime('hash_index-%Y-%m-%dT%H%M.json')
    print('writing index to ', outfile)
    with open(outfile, 'w') as fd:
        json.dump(hash_index, fd, indent=4)


if __name__ == '__main__':
    if sys.argv[1:]:
        duplicates_list, hash_index, oserror_list = check_for_duplicates(
            sys.argv[1:],
            ignore_extensions=["mp4", "avi", "mov"],
            explicit_extensions=["png", "jpg"]
        )
        dump_index(hash_index)
        import pdb; pdb.set_trace()
        remove_files(duplicates_list)
    else:
        print("Please pass the paths to check as parameters to the script")

