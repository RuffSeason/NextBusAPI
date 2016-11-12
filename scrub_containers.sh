#!/bin/bash
# Delete all containers
sudo docker rm $(docker ps -a -q)
# Delete all images
sudo docker rmi $(docker images -q)
