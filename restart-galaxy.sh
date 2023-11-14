#!/bin/bash

docker compose -f launch-galaxy.yml down
sudo cp -rf ./galaxy-tools/example /galaxy/server/tools
docker compose -f launch-galaxy.yml up -d