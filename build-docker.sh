#!/bin/bash

sed -i 's/\r$//' entrypoint.sh
IMAGE_NAME=itmir913/batchgpt

TAG=v0.0.0
docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:$TAG --push .

TAG=latest
docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:$TAG --push .
