/*
* BSD 3-Clause License
*
* Copyright 2011 Disney Enterprises, Inc.
* Copyright (c) 2019, Jacob F. Grant
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
* * Redistributions of source code must retain the above copyright notice, this
* list of conditions and the following disclaimer.
*
* * Redistributions in binary form must reproduce the above copyright notice,
* this list of conditions and the following disclaimer in the documentation
* and/or other materials provided with the distribution.
*
* * Neither the name of the copyright holders, including the names "Disney",
* "Walt Disney Pictures", "Walt Disney Animation Studios", nor the names of
* their contributors may be used to endorse or promote products derived from
* this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

'use strict';


const macos_catalogs = {
	'Darwin/8': '/content/catalogs/',
	'Darwin/9': '/content/catalogs/others/index-leopard.merged-1.',
	'Darwin/10': '/content/catalogs/others/index-leopard-snowleopard.merged-1.',
	'Darwin/11': '/content/catalogs/others/index-lion-snowleopard-leopard.merged-1.',
	'Darwin/12': '/content/catalogs/others/index-mountainlion-lion-snowleopard-leopard.merged-1.',
	'Darwin/13': '/content/catalogs/others/index-10.9-mountainlion-lion-snowleopard-leopard.merged-1.',
	'Darwin/14': '/content/catalogs/others/index-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.',
	'Darwin/15': '/content/catalogs/others/index-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.',
	'Darwin/16': '/content/catalogs/others/index-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.',
	'Darwin/17': '/content/catalogs/others/index-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.',
	'Darwin/18': '/content/catalogs/others/index-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.'
}


const os_regex = RegExp('Darwin\/\\d{1,2}', 'i');
const url_regex = RegExp('/content/catalogs/index[_\\w]*\\.sucatalog', 'i');


exports.handler = function handler(event, context, callback) {
	const request = event.Records[0].cf.request;
	const headers = request.headers;
	const user_agent = headers['user-agent'][0].value;

	// Do nothing if URL not index.sucatalog
	if (request.uri.match(url_regex) == null) {
		callback(null, request);
		return;
	}

	let catalog_url = macos_catalogs[user_agent.match(os_regex)];

	// If User Agent (OS) not found in above list, return 
	if (catalog_url == null) {
		callback(null, request);
		return;
	}
	
	request.uri = request.uri.replace('/content/catalogs/', catalog_url);
	console.log(request.uri);
	callback(null, request);
};
