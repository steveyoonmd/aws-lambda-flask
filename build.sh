#!/bin/sh

rm -rf ./bin
mkdir -p ./bin/package

cp -f *.py ./bin
# cp -f *.json ./bin
# cp -rf static ./bin

cd ./bin
pip3 install --target ./package flask

DATE=$(date '+%Y%m%d_%H%M%S')

cd ./package
zip -r9 ${OLDPWD}/bin_$DATE.zip .

cd $OLDPWD
zip -g bin_$DATE.zip *.py
