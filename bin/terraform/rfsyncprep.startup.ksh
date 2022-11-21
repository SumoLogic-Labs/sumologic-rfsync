#!/usr/bin/env bash

umask 022

outputdir="/tmp"
scriptdir="$( dirname $0 )"
terraformdir="$( cd $scriptdir ; pwd -P )"

rm -f $terraformdir/terraform.tfstate.backup 
rm -f $terraformdir/terraform.tfstate
rm -f $outputdir/rfsyncprep.output.tf

[ -d $terraformdir/.terraform ] || terraform init

terraform plan -out=$outputdir/rfsyncprep.output.tf ${varlist}
terraform apply -auto-approve ${varlist}

### rm -f $outputdir/rfsyncprep.output.tf

### terraform apply -auto-approve -destroy

### rm -f $( pwd )/terraform.tfstate.backup 
### rm -f $( pwd )/terraform.tfstate
