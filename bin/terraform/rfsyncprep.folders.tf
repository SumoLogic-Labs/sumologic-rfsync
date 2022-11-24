data "sumologic_personal_folder" "personalFolder" {}

resource "sumologic_folder" "recorded_future_base_folder" {
  name  = "recordedfuture"
  description  = "recordedfuture content, indices, and lookups"
  parent_id   = "${data.sumologic_personal_folder.personalFolder.id}"
}

output "deployment-folder-id" {
  value = "${sumologic_folder.recorded_future_base_folder.id}"
}

resource "sumologic_content_permission" "deployment-folder-permission" {
    content_id = "${sumologic_folder.recorded_future_base_folder.id}"
    notify_recipient = false
    notification_message = "no_message"

    permission {
        permission_name = "View"
        source_type = "org"
        source_id = "${var.sumologic_org_id}"

    }
}

data "local_file" "rfcontent" {
    filename = "${path.module}/json/recordedfuture_content.json"
}

resource "sumologic_content" "content" {
    parent_id = "${sumologic_folder.recorded_future_base_folder.id}"
    config = data.local_file.rfcontent.content
}

data "local_file" "rfindices" {
    filename = "${path.module}/json/recordedfuture_indices.json"
}

resource "sumologic_content" "indices" {
    parent_id = "${sumologic_folder.recorded_future_base_folder.id}"
    config = data.local_file.rfindices.content
}

resource "sumologic_folder" "lookupfolder" {
  name  = "lookups"
  description  = "recordedfuture content lookups"
  parent_id = "${sumologic_folder.recorded_future_base_folder.id}"
}

output "lookup-folder-id" {
  value = "${sumologic_folder.lookupfolder.id}"
}

resource "sumologic_content_permission" "lookup-folder-permission" {
    content_id = "${sumologic_folder.lookupfolder.id}"
    notify_recipient = false
    notification_message = "no_message"

    permission {
        permission_name = "View"
        source_type = "org"
        source_id = "${var.sumologic_org_id}"

    }
}
