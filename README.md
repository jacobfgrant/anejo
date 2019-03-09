# Anejo

A reimplementation of [Reposado](https://github.com/wdas/reposado) in Python 3 for a serverless AWS environment.


## Getting Started

Anejo is still under active development and is not production ready. You can, however, test the existing functionality. The easiest way to get stared is to use the provided [Terraform](https://www.terraform.io/) files to set up the AWS infrastructure.

* Clone the Anejo repository to your machine
* Create a `.tfvars` file with the necessary variables
* Use `terraform apply` to stand up the AWS infrastructure

And you're up and running!

## Future Development

The goal is to recreate all the functionality of Reposado running in a serverless AWS environment, with the repo hosted in S3 and served via CloudFront. If you're interested in discussing, encouraging, or helping with this project, feel free to join the [MacAdmin Slack](https://macadmins.herokuapp.com/).
