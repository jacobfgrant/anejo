### Anejo – SQS Queues ###

# Catalog Sync Queue
resource "aws_sqs_queue" "anejo_catalog_sync_queue" {
  name                       = "AnejoCatalogSyncQueue"
  visibility_timeout_seconds = 600
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0
}


# Write Local Catalog Queue
resource "aws_sqs_queue" "anejo_write_local_catalog_queue" {
  name                       = "AnejoWriteLocalCatalogQueue"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0
}


# Product Sync Queue
resource "aws_sqs_queue" "anejo_product_sync_queue" {
  name                       = "AnejoProductSyncQueue"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 600
  receive_wait_time_seconds  = 0
}
