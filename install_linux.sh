#!/bin/bash

# Install NumPy
pip3 install numpy==1.26.4

# Install ta-lib
pushd /tmp
wget https://pip.vnpy.com/colletion/ta-lib-0.4.0-src.tar.gz
tar -xf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make -j1
make install
popd

pip3 install ta-lib

# Install vnpy_evo
pip3 install vnpy_evo
pip3 install vnpy_duckdb
pip3 install vnpy_binance vnpy_btse vnpy_okx vnpy_bybit
pip3 install vnpy_novastrategy