FROM python:3.9-slim-buster

RUN mkdir -p /opt/build/appimage && \
  chmod -R ugo+rwx /opt/build && \
  apt update -y && \
  apt install -y strace patchelf fakeroot curl xz-utils \
  build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev \
  gtk-update-icon-cache && \
  python3 -m pip install appimage-builder pipenv

WORKDIR /opt/build/appimage
CMD [ "appimage-builder", "--recipe", "AppImageBuilder.yml" ]
