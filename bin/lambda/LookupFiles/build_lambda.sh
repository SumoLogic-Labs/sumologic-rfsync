#!/usr/bin/env bash

umask 022

staging="/tmp/RecordedFutureLookup-Staging"
zipfile="/tmp/RecordedFutureLookup.Package.zip"

rm -f $zipfile

mkdir -p $staging/package

cp ./lambda_function.cfg $staging
cp ./lambda_function.py $staging
cp ./domain.json $staging
cp ./hash.json $staging
cp ./ip.json $staging
cp ./url.json $staging
cp ./vulnerability.json $staging
cp ./requirements.txt $staging

cd $staging

pip3 install -r ./requirements.txt --target ./package

cd $staging/package

zip -r $zipfile .

cd $staging

zip -g $zipfile ./lambda_function.cfg
zip -g $zipfile ./lambda_function.py
zip -g $zipfile ./domain.json
zip -g $zipfile ./hash.json
zip -g $zipfile ./ip.json
zip -g $zipfile ./url.json
zip -g $zipfile ./vulnerability.json
