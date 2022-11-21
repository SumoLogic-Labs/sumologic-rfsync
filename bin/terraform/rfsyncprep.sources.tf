resource "sumologic_collector" "collector" {
  name        = "recordedfuture-collector"
  description = "recordedfuture-collector for Recorded Future map uploads"
  fields  = {
    environment = "development"
  }
}

resource "sumologic_http_source" "http_source" {
  name = "recordedfuture-source"
  description = "recordedfuture-source for Recorded Future map uploads"
  category = "myrecordedfuture/map/consolidated"
  collector_id = "${sumologic_collector.collector.id}"
}

output "collector-id" {
  value = sumologic_collector.collector.id
}

output "source-id" {
  value = sumologic_http_source.http_source.id
}

output "source-url" {
  value = sumologic_http_source.http_source.url
}
