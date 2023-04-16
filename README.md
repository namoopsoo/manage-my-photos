
# Slightly reduce your photo chaos
This repo uses others' amazing tools to help me with your photo glut. Working on a mini blog post to better describe the motivation. 

But the basic use case is if you have a main flat file directory setup where all your photos live, fed in by something like a Dropbox sync from your phone. And you want to clean up your main photo directory to be ready for showing off to other people. That means free of screenshots (`.png` files), and free of other photos that probably other people do not care about such as photos of your food ! 



## I am relying on these projects for the heavy lifting, 
https://idealo.github.io/imagededup/ , for deduping photos.

And Daniel Bourke's Food not Food repo , https://github.com/mrdbourke/food-not-food , for discriminating food photos.


## Why do you need to dedupe?
Before periodically deleting photos from my phone, I would prefer to also use the "Image Capture.app" to upload photos as a sanity check in case Dropbox did not sync everything. Uploading with "Image Capture.app" produces different filenames than on Dropbox and hence the duplication. I think after enabling "icloud photos" on my iphone, the need to manually delete photos from the phone went away for the most part.


But deduping also comes in handy for historically all the duplicated photos from the past as well as when you get photos from other people who might be giving you back your own photos say.

## Some example workflows
### Dedupe
The below will for example rm duplicates in `$main_photo_dir/2019/2019-01` and `$main_photo_dir/2019/2019-02`.

```python
main_photo_dir="/path/to/my/photos"
python strategy.py --action "dedupe"   --main-photo-dir $main_photo_dir  \
    --photo-dirs "2019/2019-01,2019/2019-02" 
```

### Separate Food Photos
(Note to run the below, you need `food-not-food` docker instance running locally, as described [below](#how-to-use-this))

Running the below will move food photos from 
`$main_photo_dir/2019/2019-01` to `$food_dir/2019/2019-01` 
and from `$main_photo_dir/2019/2019-02` to `$food_dir/2019/2019-02` .

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
The current setup involves optionally running a Docker image built from Daniel Bourke's food-not-food repo to separate food photos.

Like 

### Create docker image first 
Assuming you have Docker installed, you want to clone https://github.com/namoopsoo/food-not-food , to `/path/to/food-not-food`.

```sh
path_to_food_not_food_repo=/path/to/food-not-food
cd $path_to_food_not_food_repo

docker build -t food-not-food -f hmm-docker/Dockerfile . 
```
you should be able to see it among your docker images

```
$ docker image ls food-not-food
REPOSITORY      TAG       IMAGE ID       CREATED        SIZE
food-not-food   latest    179404e33563   5 weeks ago    5.23GB
```


### Run docker image, 
You pass the location of your main photo dir, like below, and the script `strategy.py` sends photo paths that are relative to this main photo dir.

```sh
path_to_my_main_photo_dir=/path/to/my/main/photo/dir

docker  run -i -t \
    -v $path_to_food_not_food_repo:/home \
    -v $path_to_my_main_photo_dir:/mnt/Data \
    -w /opt/server/src \
    -p 8080:8080 \
    food-not-food serve
```


# Future steps
I want to explore some few-shot-learning approaches to easily extend this wrapper to any particular category of photos that you want to move out of your main photo dir. I have taken way too many photos of my computer screen or of my whiteboard, which require manual attention, but I would love to find them automatically as well.

