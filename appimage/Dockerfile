FROM debian:buster-slim

ENV PATH "/opt/python3.9/bin:$PATH"
ENV TZ "Europe/Rome"

COPY docker-python-builder.sh /python-build.sh

# Update system
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
  apt-get update -y && apt-get upgrade -y && \
  # appimage-builder dependencies
  apt-get install -y strace patchelf fakeroot curl xz-utils gtk-update-icon-cache \
  # appimagetool dependencies
  file \
  # Python build dependencies
  build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev && \
  # workdir
  mkdir -p /opt/build/appimage && \
  chmod -R ugo+rwx /opt/build && \
  # Python 3.9
  chmod +x /python-build.sh && \
  /python-build.sh /opt/python3.9 && \
  # Install appimage-builder
  python3.9 -m pip install appimage-builder && \
  # appimagetool
  # Install appimagetool AppImage
  # See https://appimage-builder.readthedocs.io/en/latest/intro/install.html#docker
  curl -L https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage > /opt/appimagetool && \
  cd /opt/; chmod +x appimagetool; sed -i 's|AI\x02|\x00\x00\x00|' appimagetool; ./appimagetool --appimage-extract && \
  mv /opt/squashfs-root /opt/appimagetool.AppDir && \
  ln -s /opt/appimagetool.AppDir/AppRun /usr/local/bin/appimagetool


WORKDIR /opt/build/appimage

CMD [ "appimage-builder" ]
