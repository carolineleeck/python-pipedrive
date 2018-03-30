from logging import getLogger
import requests
from urllib.parse import urlencode

import json

PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1/"
logger = getLogger('pipedrive')


class PipedriveError(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return self.response.get('error', 'No error provided')


class IncorrectLoginError(PipedriveError):
    pass


class Pipedrive(object):
    def _request(self, endpoint, data, method='POST', start=0, limit=100):
        # avoid storing the string 'None' when a value is None
        data = {k: "" if v is None else v for k, v in data.items()}
        if method == "GET":
            uri = PIPEDRIVE_API_URL + endpoint + '?api_token=' + str(self.api_token)            
            if data:
                uri += '&' + urlencode(data)
            uri += '&start=' + str(start) + '&limit=' + str(limit)
            r = requests.get(uri)
        elif method == "POST":
            uri = PIPEDRIVE_API_URL + endpoint + '?api_token=' + str(self.api_token)
            r = requests.post(uri, data=data)
        elif method == "PUT":
            uri = PIPEDRIVE_API_URL + endpoint + '?api_token=' + str(self.api_token)
            r = requests.put(uri, data=data)

        logger.debug('sending {method} request to {uri}'.format(
            method=method,
            uri=uri
        ))
        
        return r.json()

    def __init__(self, api_token):
        # Assume that login is actually the api token
        self.api_token = api_token

    def __getattr__(self, name):
        def wrapper(data={}, method='GET', start=0, limit=100, params=None):
            params = params or dict()
            if params.get('deal_id'):
                response = self._request(
                    name \
                        .replace("deals", "deals_{}"
                            .format(params.get("deal_id"))) \
                        .replace('_', '/'), 
                    data, 
                    method, 
                    start=start, 
                    limit=limit
                )
            elif params.get('org_id'):
                response = self._request(
                    name \
                        .replace("organizations", "organizations_{}"
                            .format(params.get('org_id'))) \
                        .replace('_', '/'), 
                        data, 
                        method, 
                        start=start, 
                        limit=limit
                    )
            else:
                response = self._request(
                    name.replace('_', '/'), 
                    data, 
                    method, 
                    start=start, 
                    limit=limit
                )            
            return response
        return wrapper
