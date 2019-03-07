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
Common Anejo Utilities

Functions and utilities used my multiple Anejo Lambda functions.


Author:  Jacob F. Grant
Created: 01/06/19
"""

import base64
import json
import os
import plistlib
import urllib3
from urllib.parse import urlparse
import zlib

import boto3
from botocore.exceptions import ClientError


class ProvisionedThroughputExceededError(Exception):
    """Exception for exceeding DynamoDB provisioned throughput"""
    pass


# Disable urllib3 warnings
urllib3.disable_warnings()


###################
#### Functions ####
###################


### API Response Functions ###

def generate_api_response(response_code, body):
    """Return a properly formatted API response."""
    return {
        "isBase64Encoded": False,
        "statusCode": response_code,
        "headers": { "Content-Type": "application/json"},
        "body": body
    }


### AWS Utility Functions ###

def set_env_var(name, default=''):
    """Set an environmental variable or use given default value."""
    try:
        env_var = os.environ[name]
    except KeyError as e:
        env_var = str(default)
        print("Warning: Environmental variable " + str(e) + " not defined.")
        print("\t Using default value: " + env_var)
    return env_var


def s3_file_exists(file_path, bucket_name):
    """Check if file path exists in an S3 bucket."""
    try:
        boto3.client('s3').head_object(Bucket=bucket_name, Key=file_path)
    except ClientError:
        # Not found
        return False
    return True


def write_plist_s3(plist, s3_file_path, s3_bucket):
    """Write a plist to an S3 bucket."""
    boto3.client('s3').put_object(
        Body=plistlib.dumps(plist),
        Bucket=s3_bucket,
        Key=s3_file_path
    )
    return s3_file_path


def read_plist_s3(s3_file_path, s3_bucket):
    """Read a plist from an S3 bucket."""
    try:
        return plistlib.loads(
            boto3.client('s3').get_object(
                Bucket=s3_bucket,
                Key=s3_file_path
            )['Body'].read()
        )
    except boto3.client('s3').exceptions.NoSuchKey:
        print("WARNING: '" + os.path.join(s3_bucket, s3_file_path) + "' does not exist (NoSuchKey)")
        return {}


def send_to_queue(queue_message, queue_url, delay=0):
    """Send a message to an SQS queue."""
    queue_message = json.dumps(queue_message, default=str)
    return boto3.resource('sqs').Queue(queue_url).send_message(
        MessageBody=queue_message,
        DelaySeconds=int(delay)
    )



### Metadata Functions ###

def get_download_status(s3_bucket, download_status_path='metadata/DownloadStatus'):
    """Return list of downloaded product keys from directory in an S3 bucket."""
    s3_args = {
        'Bucket': s3_bucket,
        'Prefix': download_status_path
    }
    download_status = []
    while True:
        request = boto3.client('s3').list_objects_v2(**s3_args)
        # Add the base name (key) to list
        for s3_obj in request['Contents']:
            key = os.path.basename(s3_obj['Key'])
            if key:
                download_status.append(key)
        # Continue if response is truncated
        try:
            s3_args['ContinuationToken'] = request['NextContinuationToken']
        except KeyError:
            break
    return download_status


def get_catalog_branches(catalog_branches_table, names_only=False):
    """Get list of catalog branches from DynamoDB metadata table."""
    dynamodb_args = {'ConsistentRead': True}
    if names_only:
        dynamodb_args['Select'] = 'SPECIFIC_ATTRIBUTES'
        dynamodb_args['ProjectionExpression'] = 'catalog_branch'
    else:
        dynamodb_args['Select'] = 'ALL_ATTRIBUTES'

    catalog_branches = []
    while True:
        request = boto3.resource('dynamodb').Table(catalog_branches_table).scan(**dynamodb_args)
        for dynamodb_item in request['Items']:
            catalog_branches.append(dynamodb_item)
        try:
            dynamodb_args['ExclusiveStartKey'] = request['LastEvaluatedKey']
        except KeyError:
            break
    return catalog_branches


def get_default_prefs():
    """Return a dictionary of default preferences"""
    return {
        'AppleCatalogURLs': [
            ('http://swscan.apple.com/content/catalogs/'
             'index.sucatalog'),
            ('http://swscan.apple.com/content/catalogs/'
             'index-1.sucatalog'),
            ('http://swscan.apple.com/content/catalogs/others/'
             'index-leopard.merged-1.sucatalog'),
            ('http://swscan.apple.com/content/catalogs/others/'
             'index-leopard-snowleopard.merged-1.sucatalog'),
            ('http://swscan.apple.com/content/catalogs/others/'
             'index-lion-snowleopard-leopard.merged-1.sucatalog'),
            ('http://swscan.apple.com/content/catalogs/others/'
             'index-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog'),
            ('https://swscan.apple.com/content/catalogs/others/'
             'index-10.9-mountainlion-lion-snowleopard-leopard.merged-1'
             '.sucatalog'),
            ('https://swscan.apple.com/content/catalogs/others/'
             'index-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1'
             '.sucatalog'),
            ('https://swscan.apple.com/content/catalogs/others/'
             'index-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard'
             '.merged-1.sucatalog'),
            ('https://swscan.apple.com/content/catalogs/others/'
             'index-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-'
             'leopard.merged-1.sucatalog'),
            ('https://swscan.apple.com/content/catalogs/others/'
             'index-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-'
             'leopard.merged-1.sucatalog'),
            ('https://swscan.apple.com/content/catalogs/others/'
             'index-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-'
             'snowleopard-leopard.merged-1.sucatalog'),
        ],
        'PreferredLocalizations': ['English', 'en'],
        'LocalCatalogURLBase': ''
    }


def get_pref(pref_name, s3_bucket, prefs_path='metadata/Preferences.plist'):
    """Return a preference from the preference plist in S3."""
    default_prefs = get_default_prefs()
    prefs = read_plist_s3(prefs_path, s3_bucket)
    if pref_name in prefs:
        return prefs[pref_name]
    elif pref_name in default_prefs:
        return default_prefs[pref_name]
    else:
        return None


def delete_pref(pref_name, s3_bucket, prefs_path='metadata/Preferences.plist'):
    """Write a preference to the preference plist in S3."""
    prefs_plist = read_plist_s3(prefs_path, s3_bucket)
    prefs_plist.pop(pref_name, None)
    write_plist_s3(prefs_plist, prefs_path, s3_bucket)


def write_pref(pref_name, pref, s3_bucket, prefs_path='metadata/Preferences.plist'):
    """Write a preference to the preference plist in S3."""
    prefs_plist = read_plist_s3(prefs_path, s3_bucket)
    prefs_plist[pref_name] = pref
    write_plist_s3(prefs_plist, prefs_path, s3_bucket)



### Compression Utilities ###

def compress_dict(original_dict, string=False):
    """Compress a dictionary to bytes or string."""
    try:
        compressed_dict = base64.b64encode(zlib.compress(json.dumps(original_dict, default=str).encode('utf-8')))
        if string:
            compressed_dict = compressed_dict.decode('utf-8')
        return compressed_dict
    except:
        return original_dict


def uncompress_dict(original_dict):
    """Uncompress bytes or string to a dictionary."""
    try:
        original_dict = original_dict.value
    except AttributeError:
        pass
    try:
        encoded_dict = original_dict.encode('utf-8')
    except AttributeError:
        encoded_dict = original_dict
    try:
        return json.loads(zlib.decompress(base64.b64decode(encoded_dict)).decode('utf-8'))
    except:
        return original_dict



### URL Utilities ###

def get_path_from_url(url, root_dir, append_to_path=''):
    """Derive the appropriate path name based on the URL and root directory."""
    path = urlparse(url)[2]
    relative_path = path.lstrip('/')
    return os.path.join(root_dir, relative_path) + append_to_path


def retrieve_url(url):
    """Retrieve URL as bytes."""
    return urllib3.PoolManager().request(
        'GET',
        url,
        preload_content=False
    )


def replicate_url_to_bucket(url, s3_bucket, root_dir='html', append_to_path='', copy_only_if_missing=False):
    """Retrieve a URL and stores it in the same relative path in an S3 Bucket.

    Returns a path to the replicated file.
    """
    s3_file_path = get_path_from_url(url, 'html', append_to_path=append_to_path)

    if copy_only_if_missing and s3_file_exists(s3_file_path, s3_bucket):
        return s3_file_path
    else:
        print("Replicating " + url + " to " + s3_file_path)
        boto3.client('s3').upload_fileobj(
            retrieve_url(url),
            s3_bucket,
            s3_file_path
        )
        return s3_file_path



### Rewrite URLs ###

def rewrite_url(full_url, local_catalog_url_base):
    """Rewrite a URL to point to the local replica."""
    # Only rewrite the URL if necessary
    if not full_url.startswith(local_catalog_url_base):
        return get_path_from_url(full_url, local_catalog_url_base)
    else:
        return full_url


def rewrite_product_urls(product, local_catalog_url_base):
    """Rewrites all URLs for a given product."""
    if 'ServerMetadataURL' in product:
        product['ServerMetadataURL'] = rewrite_url(
            product['ServerMetadataURL'],
            local_catalog_url_base
        )
    for package in product.get('Packages', []):
        if 'URL' in package:
            package['URL'] = rewrite_url(
                package['URL'],
                local_catalog_url_base
            )
        if 'MetadataURL' in package:
            package['MetadataURL'] = rewrite_url(
                package['MetadataURL'],
                local_catalog_url_base
            )
        # Remove Digest (workaround for 10.8.2)
        if 'Digest' in package:
            del package['Digest']

    distributions = product['Distributions']
    for dist_lang in distributions.keys():
        distributions[dist_lang] = rewrite_url(
            distributions[dist_lang],
            local_catalog_url_base
        )


def rewrite_catalog_urls(catalog_plist, local_catalog_url_base):
    """Rewrites all URLs in a given catalog to point to the local replica."""
    if local_catalog_url_base is None:
        return
    if 'Products' in catalog_plist:
        product_keys = list(catalog_plist['Products'].keys())
        for product_key in product_keys:
            product = catalog_plist['Products'][product_key]
            rewrite_product_urls(product, local_catalog_url_base)



### Branch Catalogs ###

def write_branch_catalogs(local_catalog_path, s3_bucket, catalog_branches_table, product_info_table):
    """Write out branch catalogs."""
    catalog_plist = read_plist_s3(local_catalog_path, s3_bucket)
    downloaded_products = catalog_plist['Products']
    #product_info = getProductInfo()
    #
    local_catalog_name = os.path.basename(local_catalog_path)
    local_catalog_url_base = get_pref('LocalCatalogURLBase', s3_bucket)
    # now strip the '.sucatalog' bit from the name
    # so we can use it to construct our branch catalog names
    if local_catalog_path.endswith('.sucatalog'):
        local_catalog_path = local_catalog_path[0:-10]
    #
    # now write filtered catalogs (branches)
    catalog_branches = get_catalog_branches(catalog_branches_table)
    for branch in catalog_branches:
        branch_catalog_path = local_catalog_path + '_' + branch['catalog_branch'] + '.sucatalog'
        print("Building " + os.path.basename(branch_catalog_path) + "...")
        # embed branch catalog name into the catalog for troubleshooting
        # and validation
        catalog_plist['_CatalogName'] = os.path.basename(branch_catalog_path)
        catalog_plist['Products'] = {}
        for product_key in branch['product_keys']:
            if product_key in downloaded_products.keys():
                # add the product to the Products dict for this catalog
                catalog_plist['Products'][product_key] = downloaded_products[product_key]
            #elif get_pref('LocalCatalogURLBase') and product_key in product_info:
            elif local_catalog_url_base:
                try:
                    product_info = boto3.resource('dynamodb').Table(product_info_table).get_item(
                        Key={
                            'product_key': product_key
                        }
                    )['Item']
                except KeyError:
                    # Product not in ProductInfo
                    continue
                #
                # Product might have been deprecated by Apple,
                # so we check cached product info
                # Check to see if this product was ever in this
                # catalog
                original_catalogs = list(product_info.get('OriginalAppleCatalogs', []))
                for original_catalog in original_catalogs:
                    if original_catalog.endswith(local_catalog_name):
                        # this item was originally in this catalog, so
                        # we can add it to the branch
                        catalog_entry = uncompress_dict(product_info.get('CatalogEntry'))
                        title = product_info.get('title')
                        version = product_info.get('version')
                        if catalog_entry:
                            print(
                                "WARNING: Product " +
                                product_key +
                                " (" +
                                title +
                                "-" +
                                version +
                                " in branch " +
                                branch +
                                " has been deprecated. Will used cached info and packages"
                            )
                            rewrite_product_urls(catalog_entry, local_catalog_url_base)
                            catalog_plist['Products'][product_key] = catalog_entry
                            continue
            else:
                # Item not in catalog or cache - skip it
                pass
        #
        write_plist_s3(catalog_plist, branch_catalog_path, s3_bucket)



### Local Catalogs ###

def write_local_catalogs(apple_catalog_path, catalog_plist, s3_bucket, catalog_branches_table, product_info_table):
    """Write local catalogs to S3 based on the Apple catalog."""
    # Rewrite catalog URLs to point to local servers (instead of Apple's) 
    rewrite_catalog_urls(
        catalog_plist,
        get_pref('LocalCatalogURLBase', s3_bucket)
    )

    # Remove the '.apple' from the end of the catalog path
    if apple_catalog_path.endswith('.apple'):
        local_catalog_path = apple_catalog_path[0:-6]
    else:
        local_catalog_path = apple_catalog_path

    print("Building " + local_catalog_path + "...")
    catalog_plist['_CatalogName'] = os.path.basename(local_catalog_path)
    downloaded_products_list = get_download_status(s3_bucket)
    downloaded_products = {}

    product_keys = list(catalog_plist['Products'].keys())

    # Remove products that haven't been downloaded
    for product_key in product_keys:
        if product_key in downloaded_products_list:
            downloaded_products[product_key] = catalog_plist['Products'][product_key]
        else:
            print(
                "WARNING: Did not add product " +
                product_key +
                " to catalog " +
                apple_catalog_path +
                " because it has not been downloaded."
            )
    catalog_plist['Products'] = downloaded_products

    # Write raw catalog with all downloaded Apple updates enabled
    write_plist_s3(
        catalog_plist,
        local_catalog_path,
        s3_bucket
    )

    # Write filtered catalogs (branches) based on this catalog
    write_branch_catalogs(
        local_catalog_path,
        s3_bucket,
        catalog_branches_table,
        product_info_table
    )



if __name__ == "__main__":
    pass
