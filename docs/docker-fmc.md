# This document describes how to push and use the docker image of fmc tool 

## Steps to push the latest docker image
Note: This step is required only if  some changes needs to  be done to the current docker image. In  case no changes are required, the current docker image can be used and this step can be ignored.
1. Create a new branch
2. Edit the the dockerfile and/or .dockerignore file if required 
3. Raise a PR against master

Note: As soon as the PR is raised against master , it will trigger the ADO piepline **XXX-XXXX.cisco-fmc-automation** that will create and push the latest docker image to the harbor.


## Pre-requisites to pull the docker image
* Docker should be installed

## Steps to start using the fmc docker image
1. Pull the latest docker image using the below command:
   ```
    docker pull harbor.paas.xxxops.io/infrastructure/fmc:latest
   ```
2. Run the image as container
   ```
    docker run -it fmc:latest /bin/sh
   ```


