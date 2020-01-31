#!/builds/sh

rm -rf ./builds
mkdir -p ./builds/package

cp -r ./blueprints ./builds
cp -r ./libs ./builds
cp -r ./static ./builds
cp app.py ./builds

cd ./builds
pip3 install --target ./package flask

DATE=$(date '+%Y%m%d_%H%M%S_%Z')

cd ./package
zip -r9 ${OLDPWD}/build_$DATE.zip .

cd $OLDPWD
zip -r9 ./build_$DATE.zip ./blueprints
zip -r9 ./build_$DATE.zip ./libs
zip -r9 ./build_$DATE.zip ./static

zip -g build_$DATE.zip *.py

# aws lambda update-function-code --function-name my-function --zip-file fileb://build_$DATE.zip

