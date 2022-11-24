#!/usr/bin/env bash

umask 022

outputdir="/tmp"
scriptdir="$( dirname $0 )"
terraformdir="$( cd $scriptdir ; pwd -P )"

rm -f $terraformdir/terraform.tfstate.backup 
rm -f $terraformdir/terraform.tfstate
rm -f $outputdir/rfsyncprep.output.tf

[ -d $terraformdir/.terraform ] || terraform init

terraform plan -out=$outputdir/rfsyncprep.output.tf
terraform apply -auto-approve $outputdir/rfsyncprep.output.tf

cachedir=$( terraform output -raw recorded_future_cache_dir )
mkdir -p ${cachedir}/config

rm -f ${cachedir}/config/rfslconfig.cfg
echo "[Default]" >> ${cachedir}/config/rfslconfig.cfg
terraform output | sed 's/"//g' >> ${cachedir}/config/rfslconfig.cfg

cat ${cachedir}/config/rfslconfig.cfg | \
egrep -i '=' | egrep -i '(sumologic|recorded)_' | sed 's/ //g' | \
while read pair; 
do 
    varlist="-var=\"${pair}\" ${varlist}"; echo ${varlist} > ${cachedir}/config/rfslconfig.vars
done
