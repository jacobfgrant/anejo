### Anejo – API Gateway – Resource /catalogs/{catalog}/copy ###

## API Gateway Resource /catalogs/{catalog}/copy ##

# API Gateway Resource
resource "aws_api_gateway_resource" "anejo_api_catalogs_catalog_copy_resource" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  parent_id   = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_resource.id}"
  path_part   = "copy"
}
