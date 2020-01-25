#!/bin/sh

rm -rf ./bin
mkdir -p ./bin/package

cp -f *.py ./bin
# cp -f *.json ./bin
# cp -rf static ./bin

cd ./bin
pip3 install --target ./package flask

DATE=$(date '+%Y%m%d_%H%M%S_%Z')

cd ./package
zip -r9 ${OLDPWD}/bin_$DATE.zip .

cd $OLDPWD
zip -g bin_$DATE.zip *.py

# aws lambda update-function-code --function-name my-function --zip-file fileb://bin_$DATE.zip
