#!/usr/bin/env bash

umask 022

staging="/tmp/RecordedFutureLambda-DemoEvents"
zipfile="/tmp/RecordedFutureLambda-DemoEvents.Package.zip"

rm -f $zipfile

mkdir -p $staging/package

cp ./recorded_future.cfg $staging
cp ./lambda_function.py $staging
cp ./requirements.txt $staging

cd $staging

pip3 install -r ./requirements.txt --target ./package

cd $staging/package

zip -r $zipfile .

cd $staging

zip -g $zipfile ./recorded_future.cfg
zip -g $zipfile ./lambda_function.py
