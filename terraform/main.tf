##### Anejo – Main ######

### Configure local values ###

locals {
  name_extension = "${terraform.workspace == "default" ? "" : format("-%s", terraform.workspace)}"
  #name_extension = "${format("-%s", terraform.workspace)}"
  tags_map       = {
    Name        = "Anejo"
    Workspace   = "${terraform.workspace}"
    Environment = "${var.anejo_environment}"
  }
}



### Configure the AWS Providers ###

# Primary AWS Provider
provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "${var.aws_region}"
}


# AWS East (Northern Virginia) Provider
provider "aws" {
  alias      = "east"

  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "us-east-1"
}
