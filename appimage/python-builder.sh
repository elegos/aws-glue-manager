#!/usr/bin/env bash

curdir=$(pwd)
tmpdir=$(mktemp -d)
installdir="${curdir}/AppDir/usr"

mkdir -p "${installdir}"

pushd "${tmpdir}"
  curl https://www.python.org/ftp/python/3.9.2/Python-3.9.2.tar.xz > python.tar.xz
  tar xf python.tar.xz
  pushd Python-3.9.2
    ./configure --prefix "${installdir}"
    make -j $(cat /proc/cpuinfo|grep processor|wc -l) install
  popd
popd

rm -rf "${tmpdir}"
