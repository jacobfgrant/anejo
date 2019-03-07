### Anejo – API Gateway ###

# API Gateway
resource "aws_api_gateway_rest_api" "anejo_api_gateway" {
  name        = "AnejoAPI${local.name_extension}"
  description = "API Gateway for Anejo"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}


# API Gateway Deployment
resource "aws_api_gateway_deployment" "prod_deployment" {
  rest_api_id = "${aws_api_gateway_rest_api.anejo_api_gateway.id}"
  stage_name  = "prod"
  depends_on  = [
    "aws_api_gateway_integration.anejo_api_catalogs_lambda_integration",
    "aws_api_gateway_integration.anejo_api_catalogs_catalog_get_lambda_integration",
    "aws_api_gateway_integration.anejo_api_catalogs_catalog_delete_lambda_integration",
    "aws_api_gateway_integration.anejo_api_catalogs_catalog_post_lambda_integration",
    "aws_api_gateway_integration.anejo_api_catalogs_catalog_product_delete_lambda_integration",
    "aws_api_gateway_integration.anejo_api_catalogs_catalog_product_post_lambda_integration",
    "aws_api_gateway_integration.anejo_api_catalogs_catalog_copy_source_post_lambda_integration",
    "aws_api_gateway_integration.anejo_api_prefs_lambda_integration",
    "aws_api_gateway_integration.anejo_api_prefs_pref_get_lambda_integration",
    "aws_api_gateway_integration.anejo_api_prefs_pref_delete_lambda_integration",
    "aws_api_gateway_integration.anejo_api_prefs_pref_post_lambda_integration",
    "aws_api_gateway_integration.anejo_api_products_lambda_integration",
    "aws_api_gateway_integration.anejo_api_products_product_get_lambda_integration",
    "aws_api_gateway_integration.anejo_api_products_product_delete_lambda_integration",
    "aws_api_gateway_integration.anejo_api_sync_lambda_integration"
  ]
}


# Local API Gateway values
locals {
  # API Gateway Lambda Integration request template – application/json
  json_request_template = <<EOF
##  See http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
##  This template will pass through all parameters including path, querystring, header, stage variables, and context through to the integration endpoint via the body/payload
#set($allParams = $input.params())
{
"body-json" : $input.json('$'),
"params" : {
#foreach($type in $allParams.keySet())
    #set($params = $allParams.get($type))
"$type" : {
    #foreach($paramName in $params.keySet())
    "$paramName" : "$util.escapeJavaScript($params.get($paramName))"
        #if($foreach.hasNext),#end
    #end
}
    #if($foreach.hasNext),#end
#end
},
"stage-variables" : {
#foreach($key in $stageVariables.keySet())
"$key" : "$util.escapeJavaScript($stageVariables.get($key))"
    #if($foreach.hasNext),#end
#end
},
"context" : {
    "account-id" : "$context.identity.accountId",
    "api-id" : "$context.apiId",
    "api-key" : "$context.identity.apiKey",
    "authorizer-principal-id" : "$context.authorizer.principalId",
    "caller" : "$context.identity.caller",
    "cognito-authentication-provider" : "$context.identity.cognitoAuthenticationProvider",
    "cognito-authentication-type" : "$context.identity.cognitoAuthenticationType",
    "cognito-identity-id" : "$context.identity.cognitoIdentityId",
    "cognito-identity-pool-id" : "$context.identity.cognitoIdentityPoolId",
    "http-method" : "$context.httpMethod",
    "stage" : "$context.stage",
    "source-ip" : "$context.identity.sourceIp",
    "user" : "$context.identity.user",
    "user-agent" : "$context.identity.userAgent",
    "user-arn" : "$context.identity.userArn",
    "request-id" : "$context.requestId",
    "resource-id" : "$context.resourceId",
    "resource-path" : "$context.resourcePath"
    }
}

EOF
}