#!/usr/bin/env bash

fromdir="$1"
if [[ ! -d $fromdir ]]
then
    fromdir=$HOME/Pictures/sort
fi
todir="$2"
if [[ ! -d $todir ]]
then
    todir=$HOME/Pictures/year
fi


DIR=$HOME/code/smug3
cd $DIR

echo "Sorting pictures from $fromdir to $todir"


./sort_pics.py \
    --search_directory=$fromdir \
    --photo_directory=$todir \
    -v

