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
Anejo API Response – Catalogs

AWS Lambda function to responde to Anejo API Gateway requests to the /catalogs
resource and all child resources.


Author:  Jacob F. Grant
Created: 03/04/19
"""

import json

import boto3
from botocore.exceptions import ClientError

import anejocommon



### Functions ###

def get_all_catalogs(catalog_branches_table):
    """Return a dictionary of preferences"""
    catalogs = anejocommon.get_catalog_branches(catalog_branches_table, True)
    catalogs_list = []
    for catalog in catalogs:
        catalogs_list.append(catalog['catalog_branch'])
    return anejocommon.generate_api_response(200, catalogs_list)


def get_branch_catalog(catalog_name, catalog_branches_table):
    """Return single branch catalog"""
    dynamodb_args = {
        'Key': {
            'catalog_branch': catalog_name
        },
        'ConsistentRead': True
    }
    catalog = boto3.resource('dynamodb').Table(catalog_branches_table).get_item(**dynamodb_args)
    try:
        catalog_products = catalog['Item']['product_keys']
        response_code = 200
    except KeyError:
        catalog_products = 'Branch catalog does not exist'
        response_code = 404
    return anejocommon.generate_api_response(response_code, catalog_products)


def delete_branch_catalog(catalog_name, catalog_branches_table):
    """Delete a branch catalog"""
    dynamodb_args = {
        'Key': {
            'catalog_branch': catalog_name
        },
        'ReturnValues': 'NONE'
    }
    boto3.resource('dynamodb').Table(catalog_branches_table).delete_item(**dynamodb_args)
    return anejocommon.generate_api_response(200, catalog_name)


def create_branch_catalog(catalog_name, catalog_branches_table):
    """Create a branch catalog"""
    dynamodb_args = {
        'Key': {
            'catalog_branch': catalog_name
        },
        'UpdateExpression': "SET product_keys = :empty_product_keys",
        'ExpressionAttributeValues': {
            ':empty_product_keys': []
        },
        'ConditionExpression': 'attribute_not_exists(catalog_branch) AND attribute_not_exists(product_keys)'
    }
    try:
        boto3.resource('dynamodb').Table(catalog_branches_table).update_item(**dynamodb_args)
    except ClientError as e:
        # Ignore ConditionalCheckFailedExceptionother
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            return anejocommon.generate_api_response(500, str(e))
    return anejocommon.generate_api_response(200, catalog_name)


def copy_branch_catalog(catalog_name, source_catalog_name, catalog_branches_table):
    """Copy all items from one branch catalog to another"""
    # Exit with error if source catalog does not exist
    source_catalog = boto3.resource('dynamodb').Table(catalog_branches_table).get_item(
        Key={
            'catalog_branch': source_catalog_name
        },
        ConsistentRead=True
    )
    try:
        source_catalog_products = set(source_catalog['Item']['product_keys'])
    except KeyError:
        return anejocommon.generate_api_response(404, 'Source catalog does not exist')

    response = {
        'destination_catalog': catalog_name,
        'source_catalog': source_catalog_name,
        'copied_product_keys': []
    }

    # Check if catalog already exists
    catalog = boto3.resource('dynamodb').Table(catalog_branches_table).get_item(
        Key={
            'catalog_branch': catalog_name
        },
        ConsistentRead=True
    )
    try:
        catalog_products = set(catalog['Item']['product_keys'])
    except KeyError:
        catalog_products = set()

    updated_product_keys = source_catalog_products.union(catalog_products)
    if updated_product_keys != catalog_products:
        response['copied_product_keys'] = list(source_catalog_products.difference(catalog_products))
        dynamodb_args = {
            'Key': {
                'catalog_branch': catalog_name
            },
            'UpdateExpression': "SET product_keys = :updated_product_keys",
            'ExpressionAttributeValues': {
                ':updated_product_keys': list(updated_product_keys)
            }
        }
        try:
            boto3.resource('dynamodb').Table(catalog_branches_table).update_item(**dynamodb_args)
        except ClientError as e:
            return anejocommon.generate_api_response(500, str(e))
    return anejocommon.generate_api_response(200, response)


def remove_product_from_catalog(catalog_name, product_key, catalog_branches_table):
    """Remove the given product from the branch catalog"""
    response = {
        'branch_catalog': catalog_name,
        'product_key': product_key
    }

    catalog = boto3.resource('dynamodb').Table(catalog_branches_table).get_item(
        Key={
            'catalog_branch': catalog_name
        },
        ConsistentRead=True
    )
    try:
        catalog_products = set(catalog['Item']['product_keys'])
    except KeyError:
        return anejocommon.generate_api_response(404, 'Catalog does not exist')

    if product_key not in catalog_products:
        return anejocommon.generate_api_response(200, response)
    
    catalog_products.remove(product_key)
    dynamodb_args = {
        'Key': {
            'catalog_branch': catalog_name
        },
        'UpdateExpression': "SET product_keys = :updated_product_keys",
        'ExpressionAttributeValues': {
            ':updated_product_keys': list(catalog_products)
        }
    }
    try:
        boto3.resource('dynamodb').Table(catalog_branches_table).update_item(**dynamodb_args)
    except ClientError as e:
        return anejocommon.generate_api_response(500, str(e))
    return anejocommon.generate_api_response(200, response)


def add_product_to_catalog(catalog_name, product_key, catalog_branches_table):
    """Add the given product to the branch catalog"""
    response = {
        'branch_catalog': catalog_name,
        'product_key': product_key
    }

    dynamodb_args = {
        'Key': {
            'catalog_branch': catalog_name
        },
        'UpdateExpression': "SET product_keys = list_append(product_keys, :new_product_key_list)",
        'ExpressionAttributeValues': {
            ':new_product_key': product_key,
            ':new_product_key_list': [product_key]
        },
        'ConditionExpression': 'NOT contains(product_keys, :new_product_key)',
        'ReturnValues': 'ALL_NEW'
    }
    try:
        updated_catalog = boto3.resource('dynamodb').Table(catalog_branches_table).update_item(**dynamodb_args)
    except ClientError as e:
        # Ignore ConditionalCheckFailedExceptionother
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return anejocommon.generate_api_response(200, response)
        else:
            return anejocommon.generate_api_response(500, str(e))

    try:
        updated_catalog = updated_catalog['Attributes']
    except KeyError:
        return anejocommon.generate_api_response(500, 'Error adding product to catalog')
    
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
        event_body = event['body-json']
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
        catalog_name = event['params']['path']['catalog']
    except KeyError:
        catalog_name = None

    try:
        source_catalog = event['params']['path']['source']
    except KeyError:
        source_catalog = None

    try:
        product_key = event['params']['path']['product']
    except KeyError:
        product_key = None

    # /catalogs (GET)
    if (resource_path == '/catalogs' and http_method == 'GET'):
        return get_all_catalogs(CATALOG_BRANCHES_TABLE)

    # /catalogs/{catalog}
    if (resource_path == '/catalogs/{catalog}' and catalog_name):

        # GET
        if http_method == 'GET':
            return get_branch_catalog(catalog_name, CATALOG_BRANCHES_TABLE)

        # DELETE
        if http_method == 'DELETE':
            return delete_branch_catalog(catalog_name, CATALOG_BRANCHES_TABLE)

        # POST
        if http_method == 'POST':
            return create_branch_catalog(catalog_name, CATALOG_BRANCHES_TABLE)

    # /catalogs/{catalog}/copy/{source}
    if (resource_path == '/catalogs/{catalog}/copy/{source}' and catalog_name and source_catalog):
        return copy_branch_catalog(catalog_name, source_catalog, CATALOG_BRANCHES_TABLE)

    # /catalogs/{catalog}/{product}
    if (resource_path == '/catalogs/{catalog}/{product}' and catalog_name and product_key):

        # DELETE
        if http_method == 'DELETE':
            return remove_product_from_catalog(catalog_name, product_key, CATALOG_BRANCHES_TABLE)

        # POST
        if http_method == 'POST':
            return add_product_to_catalog(catalog_name, product_key, CATALOG_BRANCHES_TABLE)

    return anejocommon.generate_api_response(500, event_body)
    return anejocommon.generate_api_response(500, "Error: No matching API method found")


if __name__ == "__main__":
    pass
