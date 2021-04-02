#/usr/bin/env bash

which_podman=$(which podman 2>/dev/null)
which_docker=$(which docker 2>/dev/null)

set -e

if [ "${which_podman}" != "" ]; then
  podman build --tag aws-glue-manager-appimage-builder .
  podman run --rm --privileged \
    --volume `pwd`/..:/opt/build \
    --workdir /opt/build/appimage \
    aws-glue-manager-appimage-builder appimage-builder --skip-tests
elif [ "${which_docker}" != "" ]; then
  docker build --tag aws-glue-manager-appimage-builder .
  docker run --rm --privileged \
    --user `id -u` \
    --volume `pwd`/..:/opt/build \
    --workdir /opt/build/appimage \
    aws-glue-manager-appimage-builder appimage-builder --skip-tests
fi
