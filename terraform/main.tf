##### Anejo – Main ######

### Configure variables ###
variable "aws_access_key" {
  type        = "string"
  description = "AWS Access Key"
}

variable "aws_secret_key" {
  type        = "string"
  description = "AWS Secret Key"
}

variable "aws_region" {
  type        = "string"
  description = "AWS Region"
  default     = "us-west-1"
}

variable "zip_file_path" {
  type        = "string"
  description = "Path to .zip file containing the Lambda function"
}

variable "anejo_repo_bucket" {
  type        = "string"
  description = "S3 bucket for Anejo (Reposado)"
}

variable "anejo_write_catalog_delay" {
  type        = "string"
  description = "Time to delay rewriting catalogs"
  default     = "300"
}


### Configure the AWS Provider ###

provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "${var.aws_region}"
}
