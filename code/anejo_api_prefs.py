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
Anejo API Response – Prefs

AWS Lambda function to responde to Anejo API Gateway requests to the /prefs
resource and all child resources.


Author:  Jacob F. Grant
Created: 03/04/19
"""

import json

import anejocommon



### Functions ###

def get_all_prefs(s3_bucket, prefs_path='metadata/Preferences.plist'):
    """Return a dictionary of preferences"""
    default_prefs = anejocommon.get_default_prefs()
    prefs = anejocommon.read_plist_s3(prefs_path, s3_bucket)

    custom_prefs = list(prefs.keys())
    default_prefs_list = list(default_prefs.keys())

    for pref in default_prefs.keys():
        if pref in prefs.keys():
            default_prefs_list.remove(pref)
        else:
            prefs[pref] = default_prefs[pref]

    prefs_response = {
        'prefs': prefs,
        'custom_prefs': custom_prefs,
        'default_prefs': default_prefs_list
    }
    return anejocommon.generate_api_response(200, prefs_response)


def get_pref_value(pref_name, s3_bucket):
    """Return the value of a single preference"""
    pref = anejocommon.get_pref(pref_name, s3_bucket)
    if pref:
        response_code = 200
    else:
        response_code = 404
    return anejocommon.generate_api_response(response_code, pref)


def delete_pref_value(pref_name, s3_bucket):
    """Delete the value of a single preference"""
    anejocommon.delete_pref(pref_name, s3_bucket)
    return anejocommon.generate_api_response(200, pref_name)


def set_pref_value(pref_name, pref, s3_bucket):
    """Return the value of a single preference"""
    anejocommon.write_pref(pref_name, pref, s3_bucket)
    updated_pref = anejocommon.get_pref(pref_name, s3_bucket)
    if pref == updated_pref:
        response_code = 200
    else:
        response_code = 500
    return anejocommon.generate_api_response(response_code, updated_pref)



### HANDLER FUNCTION ###

def lambda_handler(event, context):
    """Handler function for AWS Lambda."""
    # Environmental Variables
    S3_BUCKET = anejocommon.set_env_var('S3_BUCKET')

    # Event Variables
    try:
        pref_value = event['body-json']
    except KeyError:
        pref_value = None

    try:
        event_context = event['context']
    except KeyError:
        event_context = {}
    finally:
        http_method = event_context.get('http-method', '')
        resource_path = event_context.get('resource-path', '')

    try:
        pref_name = event['params']['path']['pref']
    except KeyError:
        pref_name = None

    # /prefs (GET)
    if (resource_path == '/prefs' and http_method == 'GET'):
        return get_all_prefs(S3_BUCKET)

    # /prefs/{pref}
    if resource_path == '/prefs/{pref}' and pref_name:

        # GET
        if http_method == 'GET':
            return get_pref_value(pref_name, S3_BUCKET)

        # DELETE
        if http_method == 'DELETE':
            return delete_pref_value(pref_name, S3_BUCKET)

        # POST
        if http_method == 'POST':
            if pref_value:
                return set_pref_value(pref_name, pref_value, S3_BUCKET)
            else:
                return anejocommon.generate_api_response(400, "No pref value found")
            

    return anejocommon.generate_api_response(500, "Error: No matching API method found")


if __name__ == "__main__":
    pass
