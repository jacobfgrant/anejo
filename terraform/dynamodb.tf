### Anejo – DynamoDB Tables ###

# Anejo Product Info Table
resource "aws_dynamodb_table" "anejo_product_info_metadata" {
  name           = "AnejoProductInfo${local.name_extension}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "product_key"

  attribute {
    name = "product_key"
    type = "S"
  }

  tags = "${local.tags_map}"
}


# Anejo Catalog Branches Table
resource "aws_dynamodb_table" "anejo_catalog_branches_metadata" {
  name           = "AnejoCatalogBranches${local.name_extension}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "catalog_branch"

  attribute {
    name = "catalog_branch"
    type = "S"
  }

  tags = "${local.tags_map}"
}
