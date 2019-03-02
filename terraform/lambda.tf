### Anejo – Lambda Functions ###

## Lambda Functions ##

# Repo Sync Function
resource "aws_lambda_function" "anejo_repo_sync" {
  function_name = "anejo_repo_sync${local.name_extension}"
  description   = "Sync Anejo repo with Apple SUS"
  filename      = "${var.zip_file_path}"
  role          = "${aws_iam_role.anejo_iam_role.arn}"
  handler       = "repo_sync.lambda_handler"
  runtime       = "python3.7"
  timeout       = 60

  environment {
    variables = {
      S3_BUCKET         = "${aws_s3_bucket.anejo_repo_bucket.id}",
      CATALOG_QUEUE_URL = "${aws_sqs_queue.anejo_catalog_sync_queue.id}"
    }
  }

  tags = "${local.tags_map}"
}


# Catalog Sync Function
resource "aws_lambda_function" "anejo_catalog_sync" {
  function_name = "anejo_catalog_sync${local.name_extension}"
  description   = "Replicate Apple SUS catalog to Anejo repo"
  filename      = "${var.zip_file_path}"
  role          = "${aws_iam_role.anejo_iam_role.arn}"
  handler       = "catalog_sync.lambda_handler"
  runtime       = "python3.7"
  timeout       = 600

  environment {
    variables = {
      S3_BUCKET                  = "${aws_s3_bucket.anejo_repo_bucket.id}",
      PRODUCT_QUEUE_URL          = "${aws_sqs_queue.anejo_product_sync_queue.id}",
      PRODUCT_DOWNLOAD_QUEUE_URL = "${aws_sqs_queue.anejo_product_sync_download_queue.id}",
      WRITE_CATALOG_QUEUE_URL    = "${aws_sqs_queue.anejo_write_local_catalog_queue.id}",
      WRITE_CATALOG_DELAY        = "${var.anejo_write_catalog_delay}"
    }
  }

  tags = "${local.tags_map}"
}


# Product Sync Function
resource "aws_lambda_function" "anejo_product_sync" {
  function_name = "anejo_product_sync${local.name_extension}"
  description   = "Replicate Apple SUS product to Anejo repo"
  filename      = "${var.zip_file_path}"
  role          = "${aws_iam_role.anejo_iam_role.arn}"
  handler       = "product_sync.lambda_handler"
  runtime       = "python3.7"
  timeout       = 300
  memory_size   = 128

  environment {
    variables = {
      PRODUCT_INFO_TABLE = "${aws_dynamodb_table.anejo_product_info_metadata.id}",
      S3_BUCKET          = "${aws_s3_bucket.anejo_repo_bucket.id}"
    }
  }

  tags = "${local.tags_map}"
}


# Product Sync/Download Function
resource "aws_lambda_function" "anejo_product_sync_download" {
  function_name = "anejo_product_sync_download${local.name_extension}"
  description   = "Replicate Apple SUS product and packages to Anejo repo"
  filename      = "${var.zip_file_path}"
  role          = "${aws_iam_role.anejo_iam_role.arn}"
  handler       = "product_sync.lambda_handler"
  runtime       = "python3.7"
  timeout       = 900
  memory_size   = 512

  environment {
    variables = {
      PRODUCT_INFO_TABLE = "${aws_dynamodb_table.anejo_product_info_metadata.id}",
      S3_BUCKET          = "${aws_s3_bucket.anejo_repo_bucket.id}"
    }
  }

  tags = "${local.tags_map}"
}


# Write Local Catalog
resource "aws_lambda_function" "anejo_write_local_catalog" {
  function_name = "anejo_write_local_catalog${local.name_extension}"
  description   = "Write local catalog and branches in Anejo repo"
  filename      = "${var.zip_file_path}"
  role          = "${aws_iam_role.anejo_iam_role.arn}"
  handler       = "write_local_catalog.lambda_handler"
  runtime       = "python3.7"
  timeout       = 300

  environment {
    variables = {
      CATALOG_BRANCHES_TABLE = "${aws_dynamodb_table.anejo_catalog_branches_metadata.id}",
      PRODUCT_INFO_TABLE     = "${aws_dynamodb_table.anejo_product_info_metadata.id}",
      S3_BUCKET              = "${aws_s3_bucket.anejo_repo_bucket.id}",
    }
  }

  tags = "${local.tags_map}"
}


# URL Rewrite - Lambda@Edge
resource "aws_lambda_function" "anejo_url_rewrite" {
  provider      = "aws.east"

  function_name = "anejo_url_rewrite${local.name_extension}"
  description   = "Rewrite URL request"
  filename      = "${var.zip_file_path}"
  role          = "${aws_iam_role.anejo_iam_lambda_edge_role.arn}"
  handler       = "url_rewrite.handler"
  runtime       = "nodejs8.10"
  timeout       = 5
  publish       = true

  tags = "${local.tags_map}"
}


## Lambda Function Triggers ##

# Catalog Sync Trigger
resource "aws_lambda_event_source_mapping" "anejo_catalog_sync_trigger" {
  event_source_arn = "${aws_sqs_queue.anejo_catalog_sync_queue.arn}"
  function_name    = "${aws_lambda_function.anejo_catalog_sync.arn}"
  batch_size       = 1
}


# Products Sync Trigger
resource "aws_lambda_event_source_mapping" "anejo_product_sync_trigger" {
  event_source_arn = "${aws_sqs_queue.anejo_product_sync_queue.arn}"
  function_name    = "${aws_lambda_function.anejo_product_sync.arn}"
  batch_size       = 10
}


# Products Sync Download Trigger
resource "aws_lambda_event_source_mapping" "anejo_product_sync_download_trigger" {
  event_source_arn = "${aws_sqs_queue.anejo_product_sync_download_queue.arn}"
  function_name    = "${aws_lambda_function.anejo_product_sync_download.arn}"
  batch_size       = 1
}


# Write Local Catalog Trigger
resource "aws_lambda_event_source_mapping" "anejo_write_local_catalog_trigger" {
  event_source_arn = "${aws_sqs_queue.anejo_write_local_catalog_queue.arn}"
  function_name    = "${aws_lambda_function.anejo_write_local_catalog.arn}"
  batch_size       = 1
}
