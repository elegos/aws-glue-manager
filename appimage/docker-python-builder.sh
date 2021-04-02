#!/usr/bin/env bash

# Executed within Docker image build

tmpdir=$(mktemp -d)
installdir="$1"

mkdir -p "${installdir}"

cd "${tmpdir}"
curl https://www.python.org/ftp/python/3.9.2/Python-3.9.2.tar.xz > python.tar.xz
tar xf python.tar.xz

cd Python-3.9.2
./configure --prefix "${installdir}"
make -j $(cat /proc/cpuinfo|grep processor|wc -l) install

cd /
rm -rf "${tmpdir}"
