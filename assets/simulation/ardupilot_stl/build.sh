#!/bin/bash

name_i="ardupilot-sitl"
tag_local="test"
registry="registry.waraps.org"
name_local="$registry/$name_i:$tag_local"

docker buildx build -t $name_local --load .