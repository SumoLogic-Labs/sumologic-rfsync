#!/usr/bin/env bash

umask 022

outputdir="/tmp"

scriptdir="$( dirname $0 )"

configdir="/tmp/rfslsync_config"

terraformdir="/tmp/rfslsync_terraform"

tfcmdcount=$( which terraform | wc -l )
[[ $tfcmdcount -lt 1 ]] && exit

mkdir -p ${terraformdir}
mkdir -p ${configdir}

rm -f ${terraformdir}/terraform.tfstate.backup 
rm -f ${terraformdir}/terraform.tfstate

rm -f ${outputdir}/rfsyncprep.output.tf

rm -f ${configdir}/rfslsync.ksh
rm -f ${configdir}/rfslsync.cfg

cp -pr ${scriptdir}/. ${terraformdir}

cd ${terraformdir}

[ -d ${terraformdir}/.terraform ] || terraform init

terraform plan -out=${outputdir}/rfsyncprep.output.tf

terraform apply -auto-approve ${outputdir}/rfsyncprep.output.tf

terraform output -no-color | \
egrep -i '(sumologic|recorded)' | \
egrep -vi 'https://' | sed 's/^/export TF_VAR_/g' | \
sed 's/ = /=/g' > ${configdir}/rfslsync.ksh

echo "[Default]" >> ${configdir}/rfslsync.cfg
terraform output -no-color | sed 's/"//g' >> ${configdir}/rfslsync.cfg
