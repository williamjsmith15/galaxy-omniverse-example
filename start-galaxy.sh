#!/bin/bash

sudo mkdir -p /galaxy/server/tools
sudo cp -rf ./galaxy-tools/example /galaxy/server/tools
docker compose -f launch-galaxy.yml up -d