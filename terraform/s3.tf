### Anejo – S3 Buckets ###

# Repo S3 Bucket
resource "aws_s3_bucket" "anejo_repo_bucket" {
  bucket        = "${var.anejo_repo_bucket}"
  acl           = "private"
  force_destroy = true
}
