### Anejo – SQS Queues ###

# Catalog Sync Queue
resource "aws_sqs_queue" "anejo_catalog_sync_queue" {
  name                       = "AnejoCatalogSyncQueue${local.name_extension}"
  visibility_timeout_seconds = 600
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0
}


# Product Sync Queue
resource "aws_sqs_queue" "anejo_product_sync_queue" {
  name                       = "AnejoProductSyncQueue${local.name_extension}"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 600
  receive_wait_time_seconds  = 0
  redrive_policy             = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.anejo_product_sync_failed_queue.arn}\",\"maxReceiveCount\":3}"

  tags = "${local.tags_map}"
}


# Product Sync/Download Queue
resource "aws_sqs_queue" "anejo_product_sync_download_queue" {
  name                       = "AnejoProductSyncDownloadQueue${local.name_extension}"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0
  redrive_policy             = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.anejo_product_sync_failed_queue.arn}\",\"maxReceiveCount\":3}"

  tags = "${local.tags_map}"
}


# Product Sync Failed Queue (Dead Letter Queue)
resource "aws_sqs_queue" "anejo_product_sync_failed_queue" {
  name                       = "AnejoProductSyncFailedQueue${local.name_extension}"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 604800
  receive_wait_time_seconds  = 0

  tags = "${local.tags_map}"
}


# Write Local Catalog Queue
resource "aws_sqs_queue" "anejo_write_local_catalog_queue" {
  name                       = "AnejoWriteLocalCatalogQueue${local.name_extension}"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 900
  receive_wait_time_seconds  = 0

  tags = "${local.tags_map}"
}
