#/usr/bin/env bash

which_apt=$(which apt 2>/dev/null)
which_appimage_builder=$(which appimage-builder 2>/dev/null)
which_python3=$(which python3 2>/dev/null)
which_podman=$(which podman 2>/dev/null)
which_docker=$(which docker 2>/dev/null)

set -e

if [ ${which_apt}" != "" ] && \
   [ ${which_appimage_builder}" == "" ] && \
   [ [ ${which_podman}" == "" ] && \
   [ [ ${which_docker}" == "" ]; then
  cat << EOF
You need to install either:
  - appimage-builder
  - podman
  - docker
EOF
  exit 1
elif [ "${which_apt}" != "" ] && [ "${which_appimage_builder}" != "" ]; then
  appimage-builder --recipe AppImageBuilder.yml
elif [ "${which_podman}" != "" ]; then
  podman build --tag aws-glue-manager-appimage-builder .
  podman run --rm --privileged \
    --volume `pwd`/..:/opt/build \
    --workdir /opt/build/appimage \
    aws-glue-manager-appimage-builder
elif [ "${which_docker}" != "" ]; then
  docker build --tag aws-glue-manager-appimage-builder .
  docker run --rm --privileged \
    --user `id -u` \
    --volume `pwd`/..:/opt/build \
    --workdir /opt/build/appimage \
    aws-glue-manager-appimage-builder
fi

