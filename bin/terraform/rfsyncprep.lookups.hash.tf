resource "sumologic_lookup_table" "rf-hash-table" {
    name = "Recorded_Future_Hash_Map"
    fields {
      field_name = "Name"
      field_type = "string"
    }
    fields {
      field_name = "Algorithm"
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
    description       = "Recorded Future Hash Lookup Table"
}

output "lookuptable-rf-hash-id" {
  value = "${sumologic_lookup_table.rf-hash-table.id}"
}

resource "sumologic_content_permission" "lookuptable-rf-hash-permission" {
    content_id = "${sumologic_lookup_table.rf-hash-table.id}"
    notify_recipient = false
    notification_message = "no_message"

    permission {
        permission_name = "View"
        source_type = "org"
        source_id = "${var.sumologic_org_id}"

    }
}
