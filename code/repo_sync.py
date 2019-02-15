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
Repo Sync

AWS Lambda function that syncs the Anejo (Reposado) repo by replicating Apple
SUS catalogs and (optionally) packages to an S3 bucket.

Sends the URL of each ASUS catalog to the catalog_sync Lambda function queue.


Author:  Jacob F. Grant
Created: 01/06/19
"""

import json
from time import time

import anejocommon



### Functions ###

def catalog_sync(catalog_url, run_time, download_packages, fast_scan, catalog_queue_url):
    """Send event data to catalog_sync queue."""
    event_data = {
        'catalog_url': catalog_url,
        'run_time': run_time,
        'download_packages': download_packages,
        'fast_scan': fast_scan
    }
    print(event_data)
    anejocommon.send_to_queue(event_data, catalog_queue_url)



### HANDLER FUNCTION ###

def lambda_handler(event, context):
    """Handler function for AWS Lambda."""
    # Environmental Variables
    S3_BUCKET = anejocommon.set_env_var('S3_BUCKET')
    CATALOG_QUEUE_URL = anejocommon.set_env_var('CATALOG_QUEUE_URL')

    # Event Variables
    try:
        event_info = event['Records'][0]
    except KeyError:
        event_info = {}
    download_packages = event_info.get('download_packages', False)
    fast_scan = event_info.get('fast_scan', True)

    # Other Variables
    run_time = int(time())
    catalog_urls = anejocommon.get_pref('AppleCatalogURLs', S3_BUCKET)

    # Sync catalogs (send to SQS queue)
    for catalog_url in catalog_urls:
        catalog_sync(
            catalog_url,
            run_time,
            download_packages,
            fast_scan,
            CATALOG_QUEUE_URL
        )



if __name__ == "__main__":
    pass
