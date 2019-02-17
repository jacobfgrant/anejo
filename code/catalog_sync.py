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
Catalog Sync

AWS Lambda function that syncs one or more Apple SUS catalogs to an S3 bucket.

Sends the catalog's URL and the (compressed) data of each product therein to the
product_sync Lambda function queue. Also sends the catalog's URL to the
write_local_catalogs Lambda function queue.


Author:  Jacob F. Grant
Created: 01/06/19
"""

import json
import os
import plistlib

import boto3
from botocore.exceptions import ClientError

import anejocommon



### Functions ###

def archive_catalog(catalog_path, catalog_url, s3_bucket, index_date):
    """Make an archive copy of a catalog in S3."""
    archiver_dir = os.path.join(os.path.dirname(catalog_path), 'archive')
    catalog_name = os.path.basename(catalog_path)

    # Remove the '.apple' from the end of the catalog
    if catalog_name.endswith('.apple'):
        catalog_name = catalog_name[0:-6]
    catalog_name += index_date.strftime('.%Y-%m-%d-%H%M%S')

    archive_path = os.path.join(archiver_dir, catalog_name)
    if not anejocommon.s3_file_exists(archive_path, s3_bucket):
        try:
            boto3.client('s3').upload_fileobj(
                anejocommon.retrieve_url(catalog_url),
                s3_bucket,
                archive_path
            )
        except ClientError as e:
            print("ERROR: Cannot upload catalog to S3")
            print(str(e))
            return

    return archive_path


def product_sync(catalog_url, run_time, product_key, product_info, download_packages, fast_scan, queue_url):
    """Send event data to product_sync queue."""
    event_data = {
        'catalog_url': catalog_url,
        'run_time': run_time,
        'product_key': product_key,
        'product_info': product_info,
        'download_packages': download_packages,
        'fast_scan': fast_scan
    }
    return anejocommon.send_to_queue(event_data, queue_url)


def write_catalog(catalog_url, queue_url, delay=0):
    """Send event data to write_local_catalog queue."""
    event_data = {'catalog_url': catalog_url}
    return anejocommon.send_to_queue(event_data, queue_url, delay)



### HANDLER FUNCTION ###

def lambda_handler(event, context):
    """Handler function for AWS Lambda."""
    # Environmental Variables
    S3_BUCKET = anejocommon.set_env_var('S3_BUCKET')
    PRODUCT_QUEUE_URL = anejocommon.set_env_var('PRODUCT_QUEUE_URL')
    PRODUCT_DOWNLOAD_QUEUE_URL = anejocommon.set_env_var('PRODUCT_DOWNLOAD_QUEUE_URL')
    WRITE_CATALOG_QUEUE_URL = anejocommon.set_env_var('WRITE_CATALOG_QUEUE_URL')
    WRITE_CATALOG_DELAY = anejocommon.set_env_var('WRITE_CATALOG_DELAY', 300)

    # Loop through event records
    try:
        event_records = event['Records']
    except KeyError:
        event_records = [{'body': event}]

    for record in event_records:
        try:
            catalog_sync_info = json.loads(record['body'])
        except TypeError:
            catalog_sync_info = record['body']

        # Event Variables
        catalog_url = catalog_sync_info['catalog_url']
        run_time = catalog_sync_info['run_time']
        download_packages = catalog_sync_info.get('download_packages', False)
        fast_scan = catalog_sync_info.get('fast_scan', True)

        bucket_catalog_path = anejocommon.get_path_from_url(
            catalog_url,
            'html',
            append_to_path='.apple'
        )

        catalog = anejocommon.retrieve_url(catalog_url)
        try:
            catalog_plist = plistlib.readPlistFromBytes(catalog.data)
        except plistlib.InvalidFileException:
            print("ERROR: Cannot read catalog plist")
            return

        # Archive catalog if it already exists
        if anejocommon.s3_file_exists(bucket_catalog_path, S3_BUCKET):
            archive_catalog(
                bucket_catalog_path,
                catalog_url,
                S3_BUCKET,
                catalog_plist['IndexDate']
            )

        try:
            anejocommon.replicate_url_to_bucket(
                catalog_url,
                S3_BUCKET,
                root_dir='html',
                append_to_path='.apple'
            )
        except ClientError as e:
            print("ERROR: Cannot upload catalog to S3")
            print(str(e))
            return

        if 'Products' in catalog_plist:
            products = catalog_plist['Products']
            product_keys = list(products.keys())

            # Choose correct queue for product_sync
            if download_packages:
                queue_url = PRODUCT_DOWNLOAD_QUEUE_URL
            else:
                queue_url = PRODUCT_QUEUE_URL

            # Send to product_sync queue
            for product_key in product_keys:
                product_info = anejocommon.compress_dict(products[product_key], True)
                product_sync(
                    catalog_url,
                    run_time,
                    product_key,
                    product_info,
                    download_packages,
                    fast_scan,
                    queue_url
                )

        # Write our local (filtered) catalogs
        write_catalog(
            catalog_url,
            WRITE_CATALOG_QUEUE_URL,
            WRITE_CATALOG_DELAY
        )



if __name__ == "__main__":
    pass
