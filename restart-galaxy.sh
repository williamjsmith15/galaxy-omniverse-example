#!/bin/bash
docker compose -f launch-galaxy.yml down
sudo cp -rf ./galaxy-tools/* /galaxy/server/tools
docker compose -f launch-galaxy.yml up -d

# docker compose -f launch-galaxy.yml down && sudo cp -rf ./galaxy-tools/* /galaxy/server/tools && docker compose -f launch-galaxy.yml up -d