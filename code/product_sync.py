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
Product Sync

AWS Lambda function that syncs one or more products and (optionally) packages
from an Apple SUS catalog to an S3 bucket.

Replicates a product and (optionally) its packages to an S3 bucket and writes
the product's metadata to the product info metadata table in DynamoDB.


Author:  Jacob F. Grant
Created: 01/06/19
"""

import json
import os
import re
from xml.dom import minidom
from xml.parsers.expat import ExpatError

import boto3
from botocore.exceptions import ClientError

import anejocommon



### Functions ###

def get_preferred_localization(list_of_localizations, s3_bucket):
    """Get the preferred localization."""
    languages = anejocommon.get_pref('PreferredLocalizations', s3_bucket)
    if not languages:
        languages = ['English', 'en']

    for language in languages:
        if language in list_of_localizations:
            return language

    if 'English' in list_of_localizations:
        return 'English'
    elif 'en' in list_of_localizations:
        return 'en'
    else:
        return None


def parse_cdata(cdata_str):
    """Parse the CDATA string from an Apple Software Update distribution file
    and returns a dictionary with key/value pairs.

    The data in the CDATA string is in the format of an OS X .strings file,
    which is generally:

    "KEY1" = "VALUE1";
    "KEY2"='VALUE2';
    "KEY3" = 'A value
    that spans
    multiple lines.
    ';

    Values can span multiple lines; either single or double-quotes can be used
    to quote the keys and values, and the alternative quote character is allowed
    as a literal inside the other, otherwise the quote character is escaped.

    //-style comments and blank lines are allowed in the string; these should
    be skipped by the parser unless within a value.
    """
    # Build regex object
    REGEX = (r"""^\s*"""
             r"""(?P<key_quote>['"]?)(?P<key>[^'"]+)(?P=key_quote)"""
             r"""\s*=\s*"""
             r"""(?P<value_quote>['"])(?P<value>.*?)(?P=value_quote);$""")
    regex = re.compile(REGEX, re.MULTILINE | re.DOTALL)

    # Iterate through the CDATA string,
    # finding all possible non-overlapping matches
    parsed_data = {}
    for match_obj in re.finditer(regex, cdata_str):
        match_dict = match_obj.groupdict()
        if 'key' in match_dict.keys() and 'value' in match_dict.keys():
            key = match_dict['key']
            value = match_dict['value']
            # now 'de-escape' escaped quotes
            quote = match_dict.get('value_quote')
            if quote:
                escaped_quote = '\\' + quote
                value = value.replace(escaped_quote, quote)
            parsed_data[key] = value

    return parsed_data


def parse_software_update_dist(dist_data, debug=False):
    """Parse an Apple Software Update distribution file, looking for information
    of interest.

    Returns a dictionary containing su_name, title, version, and description.
    """
    try:
        dom = minidom.parseString(dist_data)
    except ExpatError as e:
        print("ERROR: Invalid XML dist file")
        print(str(e))
        return None

    su_choice_id_key = 'su'
    # look for <choices-outline ui='SoftwareUpdate'
    choice_outlines = dom.getElementsByTagName('choices-outline') or []
    for outline in choice_outlines:
        if 'ui' in outline.attributes.keys():
            if outline.attributes['ui'].value == 'SoftwareUpdate':
                if debug:
                    print(outline.toxml())
                lines = outline.getElementsByTagName('line')
                if lines:
                    if debug:
                        print(lines[0].toxml())
                    if 'choice' in lines[0].attributes.keys():
                        su_choice_id_key = lines[0].attributes['choice'].value

    if debug:
        print('su_choice_id_key: %s' % su_choice_id_key)

    # get values from choice id=su_choice_id_key (there may be more than one!)
    pkgs = {}
    su_choice = {}
    choice_elements = dom.getElementsByTagName('choice') or []
    for choice in choice_elements:
        keys = choice.attributes.keys()
        if 'id' in keys:
            choice_id = choice.attributes['id'].value
            if choice_id == su_choice_id_key:
                if debug:
                    print(choice.toxml())

                # this is the one Software Update uses
                for key in keys:
                    su_choice[key] = choice.attributes[key].value
                pkg_refs = choice.getElementsByTagName('pkg-ref') or []
                for pkg in pkg_refs:
                    if 'id' in pkg.attributes.keys():
                        pkg_id = pkg.attributes['id'].value
                        if not pkg_id in pkgs.keys():
                            pkgs[pkg_id] = {}
                        if pkg.firstChild:
                            pkg_name = pkg.firstChild.wholeText
                            if pkg_name:
                                pkgs[pkg_id]['name'] = pkg_name
                        if 'onConclusion' in pkg.attributes.keys():
                            pkgs[pkg_id]['RestartAction'] = (
                                pkg.attributes['onConclusion'].value)
                        if 'version' in pkg.attributes.keys():
                            pkgs[pkg_id]['version'] = (
                                pkg.attributes['version'].value)
    if debug:
        print('su_choice: %s' % su_choice)

    # look for localization and parse CDATA
    cdata = {}
    localizations = dom.getElementsByTagName('localization')
    if localizations:
        string_elements = localizations[0].getElementsByTagName('strings')
        if string_elements:
            strings = string_elements[0]
            if strings.firstChild:
                text = strings.firstChild.wholeText
                if debug:
                    print('CDATA text: %s' % text)
                cdata = parse_cdata(text)
                if debug:
                    print('CDATA dict: %s' % cdata)

    # assemble!
    dist = {}
    dist['su_name'] = su_choice.get('suDisabledGroupID', '')
    dist['title'] = su_choice.get('title', '')
    dist['version'] = su_choice.get('versStr', '')
    dist['description'] = su_choice.get('description', '')
    for key in dist.keys():
        if dist[key].startswith('SU_'):
            # get value from cdata dictionary
            dist[key] = cdata.get(dist[key], dist[key])
    dist['pkg_refs'] = pkgs

    return dist


def update_apple_catalogs(product_key, run_time, product_catalog, dynamodb_table):
    """Create/update product AppleCatalogs metadata in DynamoDB."""
    dynamodb_table = boto3.resource('dynamodb').Table(dynamodb_table)
    try:
        try:
            try:
                # If this is the first time this item has been updated for the
                # current run time, set AppleCatalogs to the current product catalog
                # and update the run time.
                request = dynamodb_table.update_item(
                    Key={
                        'product_key': product_key
                    },
                    UpdateExpression="SET run_time = :new_run_time, AppleCatalogs = :apple_catalog",
                    ExpressionAttributeValues={
                        ':new_run_time': run_time,
                        ':apple_catalog': set([product_catalog])
                    },
                    ConditionExpression=boto3.dynamodb.conditions.Attr('run_time').ne(run_time),
                    ReturnValues="UPDATED_OLD"
                )
            except boto3.resource('dynamodb').meta.client.exceptions.ConditionalCheckFailedException:
                # If this item has already been updated with the current run time,
                # add the product catalog to AppleCatalogs.
                request = dynamodb_table.update_item(
                    Key={
                        'product_key': product_key
                    },
                    UpdateExpression="ADD AppleCatalogs :apple_catalog",
                    ExpressionAttributeValues={
                        ':apple_catalog': set([product_catalog])
                    },
                    ReturnValues="UPDATED_OLD"
                )
        except boto3.resource('dynamodb').meta.client.exceptions.ProvisionedThroughputExceededException:
            print("Throughput limit exceeded. Returning products to queue.")
            request = 'ProvisionedThroughputExceededException'
            raise ProvisionedThroughputExceededError
    except ClientError as e:
        print("ERROR: Could not add item to DynamoDB")
        print(str(e))
        request = None
    return request


def update_product_metadata(product_key, product, dynamodb_table):
    """Update product metadata in DynamoDB table."""
    dynamodb_table = boto3.resource('dynamodb').Table(dynamodb_table)
    # Only update product keys that have changed
    try:
        request = dynamodb_table.get_item(
            Key={
                'product_key': product_key
            }
        )['Item']
    except ClientError as e:
        print("ERROR: Cannot retrieve item from table")
        print(str(e))
        return

    # Build update request from different keys
    update_expression = 'SET'
    expression_attribute_values = {}
    for metadata_key in [
        'title',
        'version',
        'size',
        'description',
        'PostDate',
        'pkg_refs',
        'CatalogEntry'
    ]:
        # If there is no value for the key, skip it
        if not product[metadata_key]:
            continue

        # Skip any keys that already exist
        try:
            if product[metadata_key] == anejocommon.uncompress_dict(request[metadata_key]):
                continue
        except KeyError:
            pass

        # Add value for metadata_key from product to update expression and attribute
        update_expression += (' ' + metadata_key + ' = :' + metadata_key + ',')
        expression_attribute_values[(':' + metadata_key)] = product[metadata_key]

    if len(expression_attribute_values.keys()) > 0:
        update_expression = update_expression[:-1]
    else:
        update_expression = ''

    # Add any missing values from AppleCatalogs to OriginalAppleCatalogs
    try:
        if not (set(product['AppleCatalogs']) <= set(request['OriginalAppleCatalogs'])):
            update_expression += ' ADD OriginalAppleCatalogs :original_apple_catalogs'
            expression_attribute_values[':original_apple_catalogs'] = set(product['AppleCatalogs'])
    except KeyError:
        update_expression += ' ADD OriginalAppleCatalogs :original_apple_catalogs'
        expression_attribute_values[':original_apple_catalogs'] = set(product['AppleCatalogs'])

    # Compress CatalogEntry
    try:
        expression_attribute_values[':CatalogEntry'] = anejocommon.compress_dict(
            expression_attribute_values[':CatalogEntry']
        )
    except KeyError:
        pass

    # Check if there are new keys
    if len(expression_attribute_values.keys()) > 0:
        try:
            request = dynamodb_table.update_item(
                Key={
                    'product_key': product_key
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
        except ClientError as e:
            print("ERROR: Could not update metadata")
            print(str(e))
            return None

    return request



### HANDLER FUNCTION ###

def lambda_handler(event, context):
    """Handler function for AWS Lambda."""
    # Environmental Variables
    PRODUCT_INFO_TABLE = anejocommon.set_env_var('PRODUCT_INFO_TABLE')
    S3_BUCKET = anejocommon.set_env_var('S3_BUCKET')

    # Loop through event records
    try:
        event_records = event['Records']
    except KeyError:
        event_records = [{'body': event}]

    for record in event_records:
        try:
            product_sync_info = json.loads(record['body'])
        except TypeError:
            product_sync_info = record['body']

        # Event Variables
        catalog_url = product_sync_info['catalog_url']
        run_time = product_sync_info['run_time']
        download_packages = product_sync_info.get('download_packages', False)
        fast_scan = product_sync_info.get('fast_scan', True)
        product_key = product_sync_info['product_key']
        product_info = anejocommon.uncompress_dict(product_sync_info['product_info'])

        # Update metadata table
        # Start by updating AppleCatalogs
        update_request = update_apple_catalogs(
            product_key,
            run_time,
            catalog_url,
            PRODUCT_INFO_TABLE
        )

        try:
            old_run_time = update_request['Attributes']['run_time']
        except (KeyError, TypeError):
            old_run_time = None

        # If the run time is the current one, item already updated
        if run_time != old_run_time:
            product = {}

            product['AppleCatalogs'] = set([catalog_url])
            product['CatalogEntry'] = product_info

            if download_packages and ('ServerMetadataURL' in product['CatalogEntry']):
                unused_path = anejocommon.replicate_url_to_bucket(
                    product['CatalogEntry']['ServerMetadataURL'],
                    S3_BUCKET,
                    copy_only_if_missing=fast_scan
                )
            
            if download_packages:
                for package in product['CatalogEntry'].get('Packages', []):
                    if 'URL' in package:
                        unused_path = anejocommon.replicate_url_to_bucket(
                            package['URL'],
                            S3_BUCKET,
                            copy_only_if_missing=fast_scan
                        )
                    if 'MetadataURL' in package:
                        unused_path = anejocommon.replicate_url_to_bucket(
                            package['MetadataURL'],
                            S3_BUCKET,
                            copy_only_if_missing=fast_scan
                        )

            # Calculate total size
            size = 0
            for package in product['CatalogEntry'].get('Packages', []):
                size += package.get('Size', 0)

            # Get localizations
            distributions = product['CatalogEntry']['Distributions']
            preferred_lang = get_preferred_localization(
                distributions.keys(),
                S3_BUCKET
            )
            preferred_dist = None

            for dist_lang in distributions.keys():
                dist_url = distributions[dist_lang]
                if (download_packages or dist_lang == preferred_lang):
                    dist_path = anejocommon.replicate_url_to_bucket(
                        dist_url,
                        S3_BUCKET,
                        copy_only_if_missing=fast_scan
                    )
                    if dist_lang == preferred_lang:
                        preferred_dist = anejocommon.retrieve_url(dist_url).data

            if not preferred_dist:
                print("ERROR: No usable .dist file found")
                return

            # Parse .dist file for info
            dist = parse_software_update_dist(preferred_dist)
            if not dist:
                print("ERROR: Could not get data from dist file")
                return

            product['title'] = dist['title']
            product['version'] = dist['version']
            product['size'] = size
            product['description'] = dist['description']
            product['PostDate'] = str(product['CatalogEntry']['PostDate'])
            product['pkg_refs'] = dist['pkg_refs']

            # Update product metadata
            request = update_product_metadata(
                product_key,
                product,
                PRODUCT_INFO_TABLE
            )

            # Write download status
            boto3.client('s3').put_object(
                Body='',
                Bucket=S3_BUCKET,
                Key=os.path.join('metadata/DownloadStatus', product_key)
            )



if __name__ == "__main__":
    pass
