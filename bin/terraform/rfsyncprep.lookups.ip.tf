resource "sumologic_lookup_table" "rf-ip-table" {
    name = "Recorded_Future_IP_Map"
    fields {
      field_name = "Name"
      field_type = "string"
    }
    fields {
      field_name = "Risk"
      field_type = "string"
    }
    fields {
      field_name = "RiskString"
      field_type = "string"
    }
    fields {
      field_name = "EvidenceDetails"
      field_type = "string"
    }
    ttl               = 86400
    primary_keys      = ["Name"]
    parent_folder_id = "${sumologic_folder.lookupfolder.id}"
    size_limit_action = "DeleteOldData"
    description       = "Recorded Future IP Lookup Table"
}

output "lookuptable-rf-ip-id" {
  value = "${sumologic_lookup_table.rf-ip-table.id}"
}
