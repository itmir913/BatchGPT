#!/bin/bash

IMAGE_NAME=itmir913/batchgpt
TAG=latest

docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:$TAG --push .
