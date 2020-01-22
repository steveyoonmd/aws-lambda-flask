#!/bin/sh

rm -rf ./bin
mkdir -p ./bin/package

cp -f *.py ./bin
# cp -f *.json ./bin
# cp -rf static ./bin

cd ./bin
pip3 install --target ./package flask

cd ./package
zip -r9 ${OLDPWD}/bin.zip .

cd $OLDPWD
zip -g bin.zip *.py
