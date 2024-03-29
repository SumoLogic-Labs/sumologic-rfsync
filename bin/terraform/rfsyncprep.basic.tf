terraform {
    required_providers {
        sumologic = {
            source = "sumologic/sumologic"
            version = "2.19.2" # set the Sumo Logic Terraform Provider version
        }
    }
    required_version = ">= 0.13"
}

variable "sumologic_access_id" {
  description = "Sumo Logic API Key ID"
  type        = string
}

output "sumologic_access_id" {
  value = "${var.sumologic_access_id}"
}

variable "sumologic_access_key" {
  description = "Sumo Logic API Key String"
  type        = string
}

output "sumologic_access_key" {
  value = "${var.sumologic_access_key}"
}

variable "sumologic_environment" {
  description = "Sumo Logic Deployment Location"
  type        = string
}

output "sumologic_environment" {
  value = "${var.sumologic_environment}"
}

variable "recorded_future_access_key" {
  description = "Recorded Future API Key"
  type        = string
}

output "recorded_future_access_key" {
  value = "${var.recorded_future_access_key}"
}

provider "sumologic" {
    access_id   = "${var.sumologic_access_id}"
    access_key  = "${var.sumologic_access_key}"
    environment = "${var.sumologic_environment}"
}


variable "recorded_future_cache_dir" {
  description = "Recorded Future Cache Directory"
  type        = string
}

output "recorded_future_cache_dir" {
  value = "${var.recorded_future_cache_dir}"
}

variable "sumologic_org_id" {
  description = "Sumo Logic Deployment Organizational ID"
  type        = string
}

output "sumologic_org_id" {
  value = "${var.sumologic_org_id}"
}
