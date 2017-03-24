import os
import time

import requests


class ErrorCodes:
    AUTHORIZATION_FAILED = 5
    TOO_MANY_REQUESTS = 6
    TOO_MANY_TYPICAL_REQUESTS = 9
    CAPTCHA_NEEDED = 14
    NO_ACCESS = 15
    USER_HAS_INVALID_ACCOUNT = 17
    REQUESTED_USER_DELETED_OR_BANNED = 18
    USERNAME_IS_INVALID = 113


class VkRequestError(Exception): 
    ''' Wrapper for these guys: https://vk.com/dev/errors '''

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
    ''' Both this and exchange_code_for_access_token method
        are created for this procedure: https://vk.com/dev/authcode_flow_user
    '''
    params = {'client_id': os.environ['CLIENT_ID'],
              'display': 'page',
              'redirect_uri': redirect_uri,
              'scope': 'friends',
              'response_type': 'code',
              }
    request = requests.Request('GET', 'https://oauth.vk.com/authorize', params=params)
    request.prepare()
    return request.prepare().url


def exchange_code_for_access_token(code, redirect_uri):
     ''' Both this and form_authorization_url method
         are created for this procedure: https://vk.com/dev/authcode_flow_user
     '''
     params = {'client_id': os.environ['CLIENT_ID'],
               'client_secret': os.environ['CLIENT_SECRET'],
               'redirect_uri': redirect_uri,
               'code': code,
               }
     response = requests.get('https://oauth.vk.com/access_token', params=params)
     raise_if_vk_error(response)
     return response.json().get('access_token', None)


def fetch_user(access_token, username=None, name_case='nom'):
    ''' For thorough description of the request parameters, refer to
        users.get documentation: https://vk.com/dev/users.get
    '''
    params = {'user_ids': username,
              'access_token': access_token,
              'name_case': name_case
              }
    user_list = make_vk_api_request('users.get', **params)['response']
    if len(user_list) == 0:
        return None
    return user_list[0]


def fetch_friends(access_token, count, user_id=None, offset=0):
    ''' For thorough description of the request parameters, refer to
        friends.get documentation: https://vk.com/dev/friends.get
    '''
    params = {'user_id': user_id,
              'access_token': access_token,
              'fields': 'online',
              'count': count,
              'offset': offset,
              }
    return make_vk_api_request('friends.get', **params)['response']['items']


def fetch_full_friend_list(access_token, user_id=None):
    max_friends = 5000  # VK won't return more because of 'fields' parameter
    friends = fetch_friends(access_token, max_friends, user_id)
    if len(friends) == max_friends:
        friends += fetch_friends(access_token, max_friends, user_id, offset=max_friends)
    return friends


def extract_username_from_url(user_url):
    last_slash_position = user_url.rfind('/')
    username = user_url[last_slash_position + 1:] 
    if username == '':
        return None
    return username


def fetch_online_friends(access_token, user_id=None):
    friend_list = fetch_full_friend_list(access_token, user_id)
    online_friends = []
    for friend in friend_list:
        if friend['online'] != 1:
            continue
        friend_name = ' '.join((friend['first_name'], friend['last_name']))
        friend_url = 'https://vk.com/id%d' % friend['id']
        online_friends.append({'name': friend_name, 'url': friend_url})
    return online_friends
