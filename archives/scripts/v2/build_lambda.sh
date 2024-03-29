#!/usr/bin/env bash

umask 022

staging="/tmp/RecordedFuture-Consolidated-Staging"
zipfile="/tmp/RecordedFuture-Consolidated.Package.zip"

rm -f $zipfile

mkdir -p $staging/package

cp ./rfslsetup.cfg $staging/lambda_function.cfg
cp ./rfslsetup.py $staging/lambda_function.py
cp ./sumologic.py $staging/sumologic.py
cp -r ./content $staging
cp -r ./json $staging
cp ./requirements.txt $staging

cd $staging

pip3 install -r ./requirements.txt --target ./package

cd $staging/package

zip -r $zipfile .

cd $staging

zip -g $zipfile ./lambda_function.cfg
zip -g $zipfile ./lambda_function.py
zip -g $zipfile ./sumologic.py
zip -g $zipfile ./requirements.txt
zip -r $zipfile ./content
zip -r $zipfile ./json
