import os
import time

import requests


class VkRequestError(Exception): 
    def __init__(self, message, error_code):
        super(Exception, self).__init__('%d: %s' % (error_code, message))
        self.error_code = error_code


def raise_if_vk_error(json_response):
    if 'error' in json_response:
        error_code = json_response['error']['error_code']
        error_msg = json_response['error']['error_msg']
        raise VkRequestError(error_msg, error_code)


def make_vk_api_request(method, **params):
    method_url = 'https://api.vk.com/method/%s' % method
    params['v'] = '5.62'
    response = requests.get(method_url, params=params)
    response.raise_for_status()
    json_response = response.json() 
    raise_if_vk_error(json_response)
    return json_response


def form_authorization_url(redirect_uri):
    params = {'client_id': os.environ['CLIENT_ID'],
              'display': 'page',
              'redirect_uri': redirect_uri,
              'scope': 'friends',
              'response_type': 'code',
              }
    request = requests.Request('GET', 'https://oauth.vk.com/authorize',
                               params=params)
    request.prepare()
    return request.prepare().url


def exchange_code_for_access_token(code, redirect_uri):
     params = {'client_id': os.environ['CLIENT_ID'],
               'client_secret': os.environ['CLIENT_SECRET'],
               'redirect_uri': redirect_uri,
               'code': code,
               }
     response = requests.get('https://oauth.vk.com/access_token', params=params)
     raise_if_vk_error(response)
     return response.json().get('access_token', None)


def fetch_user(access_token, username=None, name_case='nom'):
    user_list = make_vk_api_request('users.get', access_token=access_token, 
                user_ids=username)['response']
    if len(user_list) == 0:
        return None
    return user_list[0]


def fetch_friend_list(access_token, user_id=None):
    params = {'user_id': user_id,
              'access_token': access_token,
              'fields': 'nickname'
              }
    friend_list = make_vk_api_request('friends.get', **params)['response']['items']
    return friend_list


def fetch_online_friend_ids(access_token, user_id=None, online_mobile=1):
    params = {'user_id': user_id, 
              'online_mobile': 1,  # separate mobile online from desktop online
              'access_token': access_token,
              }
    online_friend_ids = make_vk_api_request('friends.getOnline', **params)
    return online_friend_ids['response']
