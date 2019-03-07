### Anejo – API Module – IAM Roles and Policies ###

## IAM Roles ##

# Anejo API IAM Lambda Role
resource "aws_iam_role" "anejo_api_iam_role" {
  name               = "anejo-api-lambda-role${local.name_extension}"
  description        = "Anejo API Lambda role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

## IAM Policies ##

# IAM Policy – CloudWatch
resource "aws_iam_role_policy" "anejo_api_cloudwatch_iam_policy" {
  name   = "AnejoAPICloudWatchPolicy${local.name_extension}"
  role   = "${aws_iam_role.anejo_api_iam_role.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
} 
EOF
}


# IAM Policy – DynamoDB
resource "aws_iam_role_policy" "anejo_api_dynamodb_iam_policy" {
  name   = "AnejoAPIDynamoDBPolicy${local.name_extension}"
  role   = "${aws_iam_role.anejo_api_iam_role.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:UpdateItem"
            ],
            "Resource": [
                "${aws_dynamodb_table.anejo_catalog_branches_metadata.arn}",
                "${aws_dynamodb_table.anejo_product_info_metadata.arn}"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "dynamodb:ListTables",
            "Resource": "*"
        }
    ]
}
EOF
}


# IAM Policy – Lambda
resource "aws_iam_role_policy" "anejo_api_lambda_iam_policy" {
  name   = "AnejoAPILambdaPolicy${local.name_extension}"
  role   = "${aws_iam_role.anejo_api_iam_role.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "lambda:ListVersionsByFunction",
                "lambda:InvokeFunction",
                "lambda:InvokeAsync"
            ],
            "Resource": "${aws_lambda_function.anejo_repo_sync.arn}"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "lambda:ListFunctions",
            "Resource": "*"
        }
    ]
}
EOF
}


# IAM Policy – S3
resource "aws_iam_role_policy" "anejo_api_s3_iam_policy" {
  name   = "AnejoAPIS3Policy${local.name_extension}"
  role   = "${aws_iam_role.anejo_api_iam_role.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "${aws_s3_bucket.anejo_repo_bucket.arn}",
                "arn:aws:s3:::*/*"
            ]
        }
    ]
}
EOF
}
