###### Anejo – Data ######


### AWS Lambda Archives ###

# AWS Lambda Archive – anejocommon
data "archive_file" "anejocommon" {
  type        = "zip"
  source_dir  = "../code/anejocommon"
  output_path = "${var.lambda_archive_dir}/anejocommon.zip"
}


# AWS Lambda Archive – anejo_api_catalogs
data "archive_file" "anejo_api_catalogs" {
  type        = "zip"
  source_file = "../code/anejo_api_catalogs.py"
  output_path = "${var.lambda_archive_dir}/anejo_api_catalogs.zip"
}


# AWS Lambda Archive – anejo_api_prefs
data "archive_file" "anejo_api_prefs" {
  type        = "zip"
  source_file = "../code/anejo_api_prefs.py"
  output_path = "${var.lambda_archive_dir}/anejo_api_prefs.zip"
}


# AWS Lambda Archive – anejo_api_products
data "archive_file" "anejo_api_products" {
  type        = "zip"
  source_file = "../code/anejo_api_products.py"
  output_path = "${var.lambda_archive_dir}/anejo_api_products.zip"
}


# AWS Lambda Archive – anejo_api_sync
data "archive_file" "anejo_api_sync" {
  type        = "zip"
  source_file = "../code/anejo_api_sync.py"
  output_path = "${var.lambda_archive_dir}/anejo_api_sync.zip"
}


# AWS Lambda Archive – catalog_sync
data "archive_file" "anejo_catalog_sync" {
  type        = "zip"
  source_file = "../code/catalog_sync.py"
  output_path = "${var.lambda_archive_dir}/catalog_sync.zip"
}


# AWS Lambda Archive – product_sync
data "archive_file" "anejo_product_sync" {
  type        = "zip"
  source_file = "../code/product_sync.py"
  output_path = "${var.lambda_archive_dir}/product_sync.zip"
}


# AWS Lambda Archive – repo_sync
data "archive_file" "anejo_repo_sync" {
  type        = "zip"
  source_file = "../code/repo_sync.py"
  output_path = "${var.lambda_archive_dir}/repo_sync.zip"
}


# AWS Lambda Archive – url_rewrite
data "archive_file" "anejo_url_rewrite" {
  type        = "zip"
  source_file = "../code/url_rewrite.js"
  output_path = "${var.lambda_archive_dir}/url_rewrite.zip"
}


# AWS Lambda Archive – write_local_catalog
data "archive_file" "anejo_write_local_catalog" {
  type        = "zip"
  source_file = "../code/write_local_catalog.py"
  output_path = "${var.lambda_archive_dir}/write_local_catalog.zip"
}
