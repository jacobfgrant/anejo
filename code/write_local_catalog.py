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
Write Local Catalog

AWS Lambda function that writes one or more local (modified) Apple SUS catalog
to an S3 bucket.

Writes a local (filtered) copy of an ASUS catalog from a given catalog's URL,
as well as writing all corresponding branch catalogs.


Author:  Jacob F. Grant
Created: 01/06/19
"""

import json
import plistlib

import anejocommon



### HANDLER FUNCTION ###

def lambda_handler(event, context):
    """Handler function for AWS Lambda."""
    # Environmental Variables
    CATALOG_BRANCHES_TABLE = anejocommon.set_env_var('CATALOG_BRANCHES_TABLE')
    S3_BUCKET = anejocommon.set_env_var('S3_BUCKET')

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

        apple_bucket_catalog_path = anejocommon.get_path_from_url(
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

        # Write our local (filtered) catalogs
        anejocommon.write_local_catalogs(
            apple_bucket_catalog_path,
            catalog_plist,
            S3_BUCKET,
            CATALOG_BRANCHES_TABLE
        )



if __name__ == "__main__":
    pass
