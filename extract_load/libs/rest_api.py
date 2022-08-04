#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2020 GoodData Corporation
import requests
from logging import Logger
from time import time, sleep
import json


class RestApi:
    def __init__(
        self,
        logger: Logger,
        endpoint,
        headers,
        wait_api_time,
        user=None,
        password=None,
        api_token=None,
        token_name='Bearer'
    ):
        self.logger = logger
        self.endpoint = endpoint
        self.headers = headers
        self.user = user
        self.password = password
        self.wait_api_time = wait_api_time
        self.api_token = api_token
        self.token_name = token_name

    def post(self, path, request, ok_code=201):
        self.logger.debug(f"POST request: {json.dumps(request)}")
        kwargs = self._prepare_request(path)
        kwargs['json'] = request
        response = requests.post(**kwargs)
        return self._resolve_return_code(response, ok_code, kwargs['url'], 'RestApi.post')

    def put(self, path, request, ok_code=204):
        self.logger.debug(f"PUT request: {json.dumps(request)}")
        kwargs = self._prepare_request(path)
        kwargs['json'] = request
        response = requests.put(**kwargs)
        return self._resolve_return_code(response, ok_code, kwargs['url'], 'RestApi.put')

    def get(self, path, params, ok_code=200):
        kwargs = self._prepare_request(path, params)
        response = requests.get(**kwargs)
        return self._resolve_return_code(response, ok_code, kwargs['url'], 'RestApi.get')

    def delete(self, path, ok_code=204, already_done_code=404):
        kwargs = self._prepare_request(path)
        response = requests.delete(**kwargs)
        if response.status_code == ok_code:
            self.logger.info(f'RestApi.delete of {path} succeeded')
            return True
        elif response.status_code == already_done_code:
            self.logger.info(f'RestApi.delete of {path} - nothing to delete')
            return True
        else:
            self.logger.error(
                f'RestApi.delete error - ' +
                f'response_code={response.status_code} message={response.text}'
            )
            return False

    def wait_for_api_is_ready(self, path):
        start = time()
        duration = 0
        while duration < self.wait_api_time:
            try:
                kwargs = self._prepare_request(path)
                response = requests.get(**kwargs)
                if response and response.status_code == 200:
                    return True
                else:
                    duration = int((time() - start) * 1000)
                    self.logger.warning(
                        f'RestApi.endpoint is not ready, retrying ... ' +
                        f'duration={duration} response_code={response.status_code} message={response.text.rstrip()}'
                    )
            except Exception as e:
                self.logger.warning(f'Hard error when connecting to endpoint - {str(e)}')
            sleep(5)
        raise Exception(f'ERROR: wait_for_api_is_ready reached timeout {self.wait_api_time}')

    def _prepare_request(self, path, params=None):
        kwargs = {
            'url': f"{self.endpoint}/{path}",
            'headers': self.headers.copy(),
        }
        if params:
            kwargs['params'] = params
        if self.api_token:
            kwargs['headers']['Authorization'] = f'{self.token_name} {self.api_token}'
        else:
            kwargs['auth'] = (self.user, self.password) if self.user is not None else None
        return kwargs

    def _resolve_return_code(self, response, ok_code, url, method):
        if response.status_code == ok_code:
            self.logger.debug(f'{method} to {url} succeeded')
            return response
        else:
            self.logger.error(
                f'{method} to {url} failed - response_code={response.status_code} message={response.text}'
            )
            return None
