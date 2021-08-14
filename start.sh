#!/bin/bash

docker build --build-arg TELEGRAMBOT_TOKEN=$TELEGRAMBOT_TOKEN -t fromsub-tg .
docker run -d -it --name fromsub-tg fromsub-tg
