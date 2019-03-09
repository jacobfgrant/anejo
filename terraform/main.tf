###### Anejo – Main ######

### Configure local values ###

locals {
  # Extension (suffix) for resource names, defined by workspace
  name_extension = "${terraform.workspace == "default" ? "" : format("-%s", terraform.workspace)}"
  
  # Name/value map for resource tags
  tags_map       = {
    Name        = "Anejo"
    Workspace   = "${terraform.workspace}"
    Environment = "${var.anejo_environment}"
  }
}



### Configure the AWS Providers ###

# Primary AWS Provider
provider "aws" {
  version    = "~> 2.1.0"

  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "${var.aws_region}"
}


# AWS East (Northern Virginia) Provider
provider "aws" {
  version    = "~> 2.1.0"
  alias      = "east"

  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "us-east-1"
}
