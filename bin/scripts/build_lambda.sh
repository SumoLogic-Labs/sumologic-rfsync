#!/usr/bin/env bash

umask 022

scriptchoice=${1:-"rfsllookups"}

staging="/tmp/RecordedFuture-SumoLogic-Staging.${scriptchoice}"
zipfile="/tmp/RecordedFuture-SumoLogic-Staging.${scriptchoice}.zip"

[ -f ./${scriptchoice}.py ] && {

	rm -f $zipfile
        rm -rf $staging

	mkdir -p $staging

	cp ./lambda_function.cfg $staging/lambda_function.cfg
	cp ./${scriptchoice}.py $staging/lambda_function.py
	cp ./requirements.txt $staging

	cd $staging

	python3 -m pip install -r ./requirements.txt --target ./package

	mkdir -p $staging/package

	cd $staging/package

	zip -r $zipfile .

	cd $staging

	zip -g $zipfile ./lambda_function.cfg
	zip -g $zipfile ./lambda_function.py
	zip -g $zipfile ./requirements.txt

}
