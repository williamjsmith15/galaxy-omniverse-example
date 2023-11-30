#!/bin/bash

sudo mkdir -p /galaxy/server/tools
sudo cp -rf ./galaxy-tools/* /galaxy/server/tools
docker compose -f launch-galaxy.yml up -d