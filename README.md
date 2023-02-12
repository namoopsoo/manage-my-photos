
# Slightly reduce photo chaos
This repo uses others amazing tools to help me with my photo glut. Working on a mini blog post to better describe the motivation. 

But the basic use case is if you have a main flat file directory setup where all your photos live, fed in by something like a Dropbox sync from your phone. And you want to clean up your main photo directory to be ready for showing off to other people. That means free of screenshots (`.png` files), and free of other photos that probably other people do not care about such as photos of your food ! 



## I am relying on these projects for the heavy lifting, 
https://idealo.github.io/imagededup/ , for deduping photos.

And Daniel Bourke's Food not Food App , https://github.com/mrdbourke/food-not-food .


## Why do you need to dedupe?
Before periodically deleting photos from my phone, I would prefer to also use the "Image Capture.app" to upload photos as a sanity check in case Dropbox did not sync everything. Uploading with "Image Capture.app" produces different filenames than on Dropbox and hence the duplication. I think after enabling "icloud photos" on my iphone, the need to manually delete photos from the phone went away for the most part.

But deduping also comes in handy for historically all the duplicated photos from the past as well as when you get photos from other people who might be giving you back your own photos say.

## Some example workflows
### Dedupe

```python
main_photo_dir="/path/to/my/photos"
python strategy.py --action "dedupe"   --main-photo-dir $main_photo_dir  \
    --photo-dirs "2019/2019-01,2019/2019-02" 
```

### Separate Food Photos
```python
main_photo_dir="/path/to/my/photos"
food_dir="/path/to/my/food/journal"
python strategy.py --action "move-food"   --main-photo-dir  $main_photo_dir   \
    --photo-dirs "2019/2019-01,2019/2019-02" \
    --food-dir $food_dir
```

### Separate png's !
```python
main_photo_dir="/path/to/my/photos"
dir_for_review="/path/to/discard/pile"
python strategy.py --action "move-pngs"   --main-photo-dir $main_photo_dir   \
    --photo-dirs "2019/2019-01,2019/2019-02" \
    --dir-for-review $dir_for_review
```


### All operations at once

```python
main_photo_dir="/path/to/my/photos"
food_dir="/path/to/my/food/journal"
dir_for_review="/path/to/discard/pile"
python strategy.py --action "move-pngs"   --main-photo-dir $main_photo_dir   \
    --photo-dirs "2019/2019-01,2019/2019-02" \
    --food-dir $food_dir \
    --dir-for-review $dir_for_review
```


# How to use this 
Current setup involves running a Docker image built from Daniel Bourke's food-not-food repo to optionally separate food photos.

Like 

### Create docker image first 
```sh
docker build -t food-not-food -f hmm-docker/Dockerfile . 

```


### Run docker image, 
```sh
path_to_food_not_food_repo=/path/to/food/not/food/repo
path_to_my_main_photo_dir=/path/to/my/main/photo/dir


docker  run -i -t \
    -v $path_to_food_not_food_repo:/home \
    -v /Users/michal/Dropbox/myphotos:/mnt/Data \
    -w /opt/server/src \
    -p 8080:8080 \
    food-not-food serve
```


