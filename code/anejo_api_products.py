# BSD 3-Clause License
#
# Copyright 2011 Disney Enterprises, Inc.
# Copyright (c) 2019, Jacob F. Grant
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders, including the names "Disney",
# "Walt Disney Pictures", "Walt Disney Animation Studios", nor the names of
# their contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Anejo API Response – Products

AWS Lambda function to responde to Anejo API Gateway requests to the /products
resource and all child resources.


Author:  Jacob F. Grant
Created: 03/04/19
"""

import json

import boto3
from botocore.exceptions import ClientError

import anejocommon



### Functions ###

def get_all_products(product_info_table):
    """Return a dictionary of preferences"""
    dynamodb_args = {
        'Select': 'SPECIFIC_ATTRIBUTES',
        'ProjectionExpression': 'product_key, title, version, PostDate',
        'ConsistentRead': True
    }
    product_info = []
    while True:
        request = boto3.resource('dynamodb').Table(product_info_table).scan(**dynamodb_args)
        for dynamodb_item in request['Items']:
            dynamodb_item['PostDate'] = dynamodb_item['PostDate'].split(' ')[0]
            product_info.append(dynamodb_item)
        try:
            dynamodb_args['ExclusiveStartKey'] = request['LastEvaluatedKey']
        except KeyError:
            break
    return anejocommon.generate_api_response(200, product_info)


def get_product_info(product_key, product_info_table):
    """Return product info"""
    dynamodb_args = {
        'Key': {
            'product_key': product_key
        },
        'ConsistentRead': True
    }
    product = boto3.resource('dynamodb').Table(product_info_table).get_item(**dynamodb_args)
    try:
        product_info = product['Item']
        product_info['CatalogEntry'] = anejocommon.uncompress_dict(product_info['CatalogEntry'])
        product_info['AppleCatalogs'] = list(product_info['AppleCatalogs'])
        product_info['OriginalAppleCatalogs'] = list(product_info['OriginalAppleCatalogs'])
        response_code = 200
    except KeyError:
        product_info = 'Product not found'
        response_code = 404
    return anejocommon.generate_api_response(response_code, product_info)












def purge_product(product_key, product_info_table, s3_bucket):
    """Purge product from Anejo"""
    response = {
            'product_key': product_key,
            'product_info': None,
            'deleted_objects': None
        }

    # Get product info, return if product not found
    dynamodb_args = {
        'Key': {
            'product_key': product_key
        },
        'ConsistentRead': True
    }
    product = boto3.resource('dynamodb').Table(product_info_table).get_item(**dynamodb_args)
    try:
        product_info = product['Item']
        product_info['CatalogEntry'] = anejocommon.uncompress_dict(product_info['CatalogEntry'])
        product_info['AppleCatalogs'] = list(product_info['AppleCatalogs'])
        product_info['OriginalAppleCatalogs'] = list(product_info['OriginalAppleCatalogs'])
    except KeyError:
        return anejocommon.generate_api_response(200, response)

    # Get list of all objects to delete from S3 bucket
    objects_to_purge = []
    if 'ServerMetadataURL' in product_info['CatalogEntry']:
        objects_to_purge.append(
            {
                'Key': anejocommon.get_path_from_url(
                    product_info['CatalogEntry']['ServerMetadataURL'],
                    'html'
                )
            }
        )
    for package in product_info['CatalogEntry'].get('Packages', []):
        if 'URL' in package:
            objects_to_purge.append(
                {
                    'Key': anejocommon.get_path_from_url(
                        package['URL'],
                        'html'
                    )
                }
            )
        if 'MetadataURL' in package:
            objects_to_purge.append(
                {
                    'Key': anejocommon.get_path_from_url(
                        package['MetadataURL'],
                        'html'
                    )
                }
            )
    distributions = product_info['CatalogEntry']['Distributions']
    for dist_lang in distributions.keys():
        dist_url = distributions[dist_lang]
        objects_to_purge.append(
            {
                'Key': anejocommon.get_path_from_url(
                    dist_url,
                    'html'
                )
            }
        )

    # Attempt to delete objects from S3
    try:
        purged_objects = boto3.client('s3').delete_objects(
            Bucket=s3_bucket,
            Delete={
                'Objects': objects_to_purge
            }
        )['Deleted']
    except ClientError as e:
        return anejocommon.generate_api_response(500, str(e))
    
    response['product_info'] = product_info
    response['deleted_objects'] = purged_objects
    
    # Delete product from Product Info metadata table
    del dynamodb_args['ConsistentRead']
    dynamodb_args['ReturnValues'] = 'ALL_OLD'
    try:
        product = boto3.resource('dynamodb').Table(product_info_table).delete_item(**dynamodb_args)
    except ClientError as e:
        return anejocommon.generate_api_response(500, str(e))
    return anejocommon.generate_api_response(200, response)



### HANDLER FUNCTION ###

def lambda_handler(event, context):
    """Handler function for AWS Lambda."""
    # Environmental Variables
    CATALOG_BRANCHES_TABLE = anejocommon.set_env_var('CATALOG_BRANCHES_TABLE')
    PRODUCT_INFO_TABLE = anejocommon.set_env_var('PRODUCT_INFO_TABLE')
    S3_BUCKET = anejocommon.set_env_var('S3_BUCKET')

    # Event Variables
    try:
        event_body = event['body']
    except KeyError:
        event_body = event

    try:
        event_context = event['context']
    except KeyError:
        event_context = {}
    finally:
        http_method = event_context.get('http-method', '')
        resource_path = event_context.get('resource-path', '')

    try:
        product_key = event['params']['path']['product']
    except KeyError:
        product_key = None

    # /products (GET)
    if (resource_path == '/products' and http_method == 'GET'):
        return get_all_products(PRODUCT_INFO_TABLE)

    # /products/{product}
    if (resource_path == '/products/{product}' and product_key):

        # GET
        if http_method == 'GET':
            return get_product_info(product_key, PRODUCT_INFO_TABLE)

        # DELETE
        if http_method == 'DELETE':
            return purge_product(product_key, PRODUCT_INFO_TABLE, S3_BUCKET)


if __name__ == "__main__":
    pass
