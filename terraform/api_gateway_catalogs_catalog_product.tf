### Anejo – API Gateway – Resource /catalogs/{catalog}/{product} ###


## API Gateway Resource ##

# API Gateway Resource
resource "aws_api_gateway_resource" "anejo_api_catalogs_catalog_product_resource" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  parent_id   = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_resource.id}"
  path_part   = "{product}"
}



## API Gateway Resource – DELETE Method ##

# API Gateway Method (DELETE)
resource "aws_api_gateway_method" "anejo_api_catalogs_catalog_product_delete" {
  rest_api_id   = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id   = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method   = "DELETE"
  authorization = "NONE"
}


# API Gateway Lambda Integration (DELETE) – Anejo API Prefs Lambda function
resource "aws_api_gateway_integration" "anejo_api_catalogs_catalog_product_delete_lambda_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id             = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method             = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_delete.http_method}"
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.anejo_api_catalogs.arn}/invocations"

  passthrough_behavior = "WHEN_NO_TEMPLATES"
  request_templates    = {
    "application/json" = "${local.json_request_template}"
  }
}


# API Gateway Lambda Permission (DELETE) – Anejo API Prefs Lambda function
resource "aws_lambda_permission" "anejo_api_catalogs_catalog_product_delete_lambda_permission" {
  statement_id_prefix  = "AllowAPIGatewayInvoke"
  action               = "lambda:InvokeFunction"
  function_name        = "${aws_lambda_function.anejo_api_catalogs.arn}"
  principal            = "apigateway.amazonaws.com"
  source_arn           = "${aws_api_gateway_rest_api.anejo_api_gateway.execution_arn}/*/DELETE/catalogs/{catalog}/{product}"
}


# API Gateway Method Response (DELETE) – HTTP 200
resource "aws_api_gateway_method_response" "api_catalogs_catalog_product_delete_http_200_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_delete.http_method}"
  status_code = "200"
}


# API Gateway Lambda Integration Response (DELETE) – HTTP 200
resource "aws_api_gateway_integration_response" "api_catalogs_catalog_product_delete_http_200_lambda_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_delete.http_method}"
  status_code = "${aws_api_gateway_method_response.api_catalogs_catalog_product_delete_http_200_response.status_code}"

  depends_on  = ["aws_api_gateway_integration.anejo_api_catalogs_catalog_product_delete_lambda_integration"]
}


# API Gateway Method Response (DELETE) – HTTP 500
resource "aws_api_gateway_method_response" "api_catalogs_catalog_product_delete_http_500_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_delete.http_method}"
  status_code = "500"
}


# API Gateway Lambda Integration Response (DELETE) – HTTP 500
resource "aws_api_gateway_integration_response" "api_catalogs_catalog_product_delete_http_500_lambda_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_delete.http_method}"
  status_code = "${aws_api_gateway_method_response.api_catalogs_catalog_product_delete_http_500_response.status_code}"

  selection_pattern = "${var.anejo_http_500_response_pattern}"

  depends_on  = ["aws_api_gateway_integration.anejo_api_catalogs_catalog_product_delete_lambda_integration"]
}



## API Gateway Resource – POST Method ##

# API Gateway Method (POST)
resource "aws_api_gateway_method" "anejo_api_catalogs_catalog_product_post" {
  rest_api_id   = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id   = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method   = "POST"
  authorization = "NONE"
}


# API Gateway Lambda Integration (POST) – Anejo API Prefs Lambda function
resource "aws_api_gateway_integration" "anejo_api_catalogs_catalog_product_post_lambda_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id             = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method             = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_post.http_method}"
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.anejo_api_catalogs.arn}/invocations"

  passthrough_behavior = "WHEN_NO_TEMPLATES"
  request_templates    = {
    "application/json" = "${local.json_request_template}"
  }
}


# API Gateway Lambda Permission (POST) – Anejo API Prefs Lambda function
resource "aws_lambda_permission" "anejo_api_catalogs_catalog_product_post_lambda_permission" {
  statement_id_prefix  = "AllowAPIGatewayInvoke"
  action               = "lambda:InvokeFunction"
  function_name        = "${aws_lambda_function.anejo_api_catalogs.arn}"
  principal            = "apigateway.amazonaws.com"
  source_arn           = "${aws_api_gateway_rest_api.anejo_api_gateway.execution_arn}/*/POST/catalogs/{catalog}/{product}"
}


# API Gateway Method Response (POST) – HTTP 200
resource "aws_api_gateway_method_response" "api_catalogs_catalog_product_post_http_200_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_post.http_method}"
  status_code = "200"
}


# API Gateway Lambda Integration Response (POST) – HTTP 200
resource "aws_api_gateway_integration_response" "api_catalogs_catalog_product_post_http_200_lambda_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_post.http_method}"
  status_code = "${aws_api_gateway_method_response.api_catalogs_catalog_product_post_http_200_response.status_code}"

  depends_on  = ["aws_api_gateway_integration.anejo_api_catalogs_catalog_product_post_lambda_integration"]
}


# API Gateway Method Response (POST) – HTTP 500
resource "aws_api_gateway_method_response" "api_catalogs_catalog_product_post_http_500_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_post.http_method}"
  status_code = "500"
}


# API Gateway Lambda Integration Response (POST) – HTTP 500
resource "aws_api_gateway_integration_response" "api_catalogs_catalog_product_post_http_500_lambda_response" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  resource_id = "${aws_api_gateway_resource.anejo_api_catalogs_catalog_product_resource.id}"
  http_method = "${aws_api_gateway_method.anejo_api_catalogs_catalog_product_post.http_method}"
  status_code = "${aws_api_gateway_method_response.api_catalogs_catalog_product_post_http_500_response.status_code}"

  selection_pattern = "${var.anejo_http_500_response_pattern}"

  depends_on  = ["aws_api_gateway_integration.anejo_api_catalogs_catalog_product_post_lambda_integration"]
}
