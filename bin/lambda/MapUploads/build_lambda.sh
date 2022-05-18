#!/usr/bin/env bash

umask 022

staging="/tmp/RecordedFutureLambda-Upload"
zipfile="/tmp/RecordedFutureLambda-Upload.Package.zip"

rm -f $zipfile

mkdir -p $staging/package

cp ./lambda_function.cfg $staging
cp ./lambda_function.py $staging
cp ./requirements.txt $staging
cp ./requirements.txt $staging

cd $staging

pip3 install -r ./requirements.txt --target ./package

cd $staging/package

zip -r $zipfile .

cd $staging

zip -g $zipfile ./lambda_function.cfg
zip -g $zipfile ./lambda_function.py
