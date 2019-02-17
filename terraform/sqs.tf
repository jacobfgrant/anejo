### Anejo – SQS Queues ###

# Catalog Sync Queue
resource "aws_sqs_queue" "anejo_catalog_sync_queue" {
  name                       = "AnejoCatalogSyncQueue"
  visibility_timeout_seconds = 600
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0
}


# Product Sync Queue
resource "aws_sqs_queue" "anejo_product_sync_queue" {
  name                       = "AnejoProductSyncQueue"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 600
  receive_wait_time_seconds  = 0
  redrive_policy             = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.anejo_product_sync_failed_queue.arn}\",\"maxReceiveCount\":3}"
}


# Product Sync/Download Queue
resource "aws_sqs_queue" "anejo_product_sync_download_queue" {
  name                       = "AnejoProductSyncDownloadQueue"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0
  redrive_policy             = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.anejo_product_sync_failed_queue.arn}\",\"maxReceiveCount\":3}"
}


# Product Sync Failed Queue (Dead Letter Queue)
resource "aws_sqs_queue" "anejo_product_sync_failed_queue" {
  name                       = "AnejoProductSyncFailedQueue"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 604800
  receive_wait_time_seconds  = 0
}


# Write Local Catalog Queue
resource "aws_sqs_queue" "anejo_write_local_catalog_queue" {
  name                       = "AnejoWriteLocalCatalogQueue"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0
}
