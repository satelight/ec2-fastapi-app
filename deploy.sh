#!/bin/bash
set -e

BUCKET="fastapi-files-20260816"
COMMIT_ID=$1
APP_DIR="/home/ec2-user/fastapi-app"
BUILD_DIR="/tmp/fastapi-build"

if [ -z "$COMMIT_ID" ]; then
  echo "Error: COMMIT_ID is required"
  exit 1
fi

mkdir -p $BUILD_DIR
cd $BUILD_DIR
aws s3 cp s3://$BUCKET/builds/app-$COMMIT_ID.tar.gz .
if [ -d "$APP_DIR" ]; then
  sudo mv $APP_DIR ${APP_DIR}.backup.$(date +%s)
fi
mkdir -p $APP_DIR
tar -xzf app-$COMMIT_ID.tar.gz -C $APP_DIR
cd $APP_DIR

# ???????????
uv sync

sudo systemctl restart fastapi
echo "Deployment complete!"
