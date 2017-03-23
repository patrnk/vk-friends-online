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
    request = requests.Request('GET', 'https://oauth.vk.com/authorize',
                               params=params)
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


def fetch_friend_names(access_token, count, user_id=None, offset=0):
    ''' For thorough description of the request parameters, refer to
        friends.get documentation: https://vk.com/dev/friends.get
    '''
    params = {'user_id': user_id,
              'access_token': access_token,
              'fields': 'nickname',  # this way we can get the names of the friends
              'count': count,
              'offset': offset,
              }
    return make_vk_api_request('friends.get', **params)['response']['items']


def fetch_friend_list(access_token, user_id=None):
    max_friends = 5000  # VK won't return more because of 'fields' parameter
    friends = fetch_friend_names(access_token, max_friends, user_id)
    if len(friends) == max_friends:
        friends += fetch_friend_names(access_token, max_friends, user_id, 
                                      offset=max_friends)
    return friends


def fetch_online_friend_ids(access_token, user_id=None, online_mobile=1):
    ''' For thorough description of the request parameters, refer to
        friends.getOnline documentation: https://vk.com/dev/friends.getOnline
    '''
    params = {'user_id': user_id, 
              'online_mobile': 1,  # separate mobile online from desktop online
              'access_token': access_token,
              }
    online_friend_ids = make_vk_api_request('friends.getOnline', **params)
    return online_friend_ids['response']


def extract_username_from_url(user_url):
    last_slash_position = user_url.rfind('/')
    username = user_url[last_slash_position + 1:] 
    if username == '':
        return None
    return username


def turn_friend_list_into_dictionary(friend_list):
    friends = {}
    for friend in friend_list:
        friends[friend['id']] = friend
    return friends


def fetch_online_friends(access_token, user_id=None):
    friend_list = fetch_friend_list(access_token, user_id)
    friends = turn_friend_list_into_dictionary(friend_list)
    online_friend_ids = fetch_online_friend_ids(access_token, user_id)
    online_desktop_ids = online_friend_ids['online']
    online_mobile_ids = online_friend_ids['online_mobile']
    online_friends = []
    for online_id in online_desktop_ids + online_mobile_ids:
        friend = friends[online_id]
        friend_name = ' '.join((friend['first_name'], friend['last_name']))
        online_friends.append({'name': friend_name,
                               'url': 'https://vk.com/id%d' % online_id,
                               'mobile': online_id in online_mobile_ids})
    return online_friends
