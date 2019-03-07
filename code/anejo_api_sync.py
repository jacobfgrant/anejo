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
Anejo API Response – Sync

AWS Lambda function to responde to Anejo API Gateway requests to the /sync
resource and all child resources.


Author:  Jacob F. Grant
Created: 03/04/19
"""

import json

import boto3
from botocore.exceptions import ClientError

import anejocommon



### HANDLER FUNCTION ###

def lambda_handler(event, context):
    """Handler function for AWS Lambda."""
    # Environmental Variables
    REPO_SYNC_FUNCTION = anejocommon.set_env_var('REPO_SYNC_FUNCTION')

    # Event Variables
    try:
        event_body = event['body-json']
    except KeyError:
        event_body = event

    repo_sync_parameters = {}
    try:
        repo_sync_parameters['download_packages'] = event_body['download_packages']
    except KeyError:
        pass

    try:
        repo_sync_parameters['fast_scan'] = event_body['fast_scan']
    except KeyError:
        pass

    try:
        lambda_call = boto3.client('lambda').invoke(
            FunctionName=REPO_SYNC_FUNCTION,
            InvocationType='Event',
            LogType='None',
            Payload=json.dumps(repo_sync_parameters)
        )
    except ClientError as e:
        lambda_call = {
            'StatusCode': 406,
            'FunctionError': str(e)
        }

    response_code = lambda_call['StatusCode']
    if(response_code == 200 or response_code == 202):
        response_body = 'Accepted/Success'
    else:
        try:
            response_body = lambda_call['FunctionError']
        except KeyError:
            response_body = 'Error/Failure'

    return anejocommon.generate_api_response(response_code, response_body)



if __name__ == "__main__":
    pass
