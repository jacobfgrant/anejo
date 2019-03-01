### Anejo – S3 Buckets ###

# Anejo Repo S3 Bucket
resource "aws_s3_bucket" "anejo_repo_bucket" {
  bucket        = "${var.anejo_repo_bucket}${local.name_extension}"
  acl           = "private"
  force_destroy = true

  tags = "${local.tags_map}"
}


# Anejo S3 Bucket Policy
resource "aws_s3_bucket_policy" "anejo_s3_bucket_policy" {
  bucket = "${aws_s3_bucket.anejo_repo_bucket.id}"
  policy = "${data.aws_iam_policy_document.anejo_s3_bucket_policy_document.json}"
}
