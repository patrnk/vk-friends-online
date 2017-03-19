from . import vk_api


def extract_username_from_url(user_url):
    last_slash_position = user_url.rfind('/')
    return user_url[last_slash_position + 1:]


def turn_friend_list_into_dictionary(friend_list):
    friends = {}
    for friend in friend_list:
        friends[friend['id']] = friend
    return friends


def fetch_online_friends(access_token, user_id=None):
    friend_list = vk_api.fetch_friend_list(access_token, user_id)
    friends = turn_friend_list_into_dictionary(friend_list)
    online_friend_ids = vk_api.fetch_online_friend_ids(access_token, user_id)
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
