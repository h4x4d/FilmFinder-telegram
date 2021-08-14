#!/bin/bash

docker rm $(docker stop fromsub-tg)
docker image rm fromsub-tg
