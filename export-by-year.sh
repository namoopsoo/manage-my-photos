#!/bin/bash

PHOTO_DIR="$HOME/Pictures/Photos Library.photoslibrary/originals"
YEAR_TMP="/tmp/exif-years"


usage() {
  echo "Usage: $0  [--year YEAR] "
  exit 1
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --year)
      TARGET_YEAR="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

if [[ -z "$TARGET_YEAR" ]]; then 
    usage
    exit 0
fi

mkdir -p "$YEAR_TMP"

echo "using temp $YEAR_TMP"

echo "🔍 Scanning for photos by EXIF year..."

# Extract EXIF year and copy into /tmp/year directories
find "$PHOTO_DIR" -type f -iname '*.jpg' -o -iname '*.heic' -o -iname '*.jpeg' -o -iname '*.png' | while read -r file; do
    year=$(exiftool -s3 -DateTimeOriginal "$file" | cut -d':' -f1)

    if [[ -z "$year" ]]; then
        # fallback to file mod year
        year=$(date -r "$file" +%Y)
    fi

    if [[ "$year" != $TARGET_YEAR ]]; then
        continue
    fi

    mkdir -p "$YEAR_TMP/$year"
    cp "$file" "$YEAR_TMP/$year/"
    
done

echo "✅ Organized by year into: $YEAR_TMP"

# Now upload one year at a time
for yeardir in "$YEAR_TMP"/*; do
    year=$(basename "$yeardir")
    echo "🚀 Uploading year: $year"

    immich upload "$yeardir" --recursive 

    echo "🧹 Deleting temp folder for $year"
    rm -rf "$yeardir"
done
