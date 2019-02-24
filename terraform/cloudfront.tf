### Anejo – CloudFront Distribution ###


locals {
  anejo_s3_origin_id = "AnejoS3Origin"
}



resource "aws_cloudfront_origin_access_identity" "anejo_distribution_identity" {
  comment = "Origin Access Identity for Anejo S3 bucket origin."
}


# CloudFront Distribution
resource "aws_cloudfront_distribution" "anejo_distribution" {
  origin {
    domain_name = "${aws_s3_bucket.anejo_repo_bucket.bucket_regional_domain_name}"
    origin_id   = "${local.anejo_s3_origin_id}"
    origin_path = "/html"

    s3_origin_config {
      origin_access_identity = "${aws_cloudfront_origin_access_identity.anejo_distribution_identity.cloudfront_access_identity_path}"
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Anejo CloudFront distribution"

  logging_config {
    include_cookies = false
    bucket          = "${aws_s3_bucket.anejo_repo_bucket.bucket_domain_name}",
    prefix          = "logs/distribution/"
  }

  aliases = "${var.anejo_distribution_aliases}"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "${local.anejo_s3_origin_id}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # Lambda@Edge URL Rewrite
  ordered_cache_behavior {
    path_pattern     = "*index*.sucatalog"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "${local.anejo_s3_origin_id}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    lambda_function_association {
      event_type   = "origin-request"
      lambda_arn   = "${aws_lambda_function.example.qualified_arn}"
      include_body = true
    }
  }

    # Cache behavior for catalogs
  ordered_cache_behavior {
    path_pattern     = "*.sucatalog"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "${local.anejo_s3_origin_id}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 600
    max_ttl                = 3600
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = "${var.anejo_distribution_geo_restriction_whitelist}"
    }
  }

  tags = "${local.tags_map}"

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
