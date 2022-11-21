#!/usr/bin/env bash

umask 022

staging="/tmp/RecordedFuture-Consolidated-Staging"
zipfile="/tmp/RecordedFuture-Consolidated.Package.zip"

rm -f $zipfile

mkdir -p $staging/package

cp ./rfsllookups.cfg $staging/lambda_function.cfg
cp ./rfsllookups.py $staging/lambda_function.py
cp ./requirements.txt $staging

cd $staging

python3 -m pip3 install -r ./requirements.txt --target ./package

cd $staging/package

zip -r $zipfile .

cd $staging

zip -g $zipfile ./lambda_function.cfg
zip -g $zipfile ./lambda_function.py
zip -g $zipfile ./requirements.txt
