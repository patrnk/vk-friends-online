from . import vk_api


def extract_username_from_url(user_url):
    last_slash_position = user_url.rfind('/')
    return user_url[last_slash_position + 1:]


def fetch_online_friends(access_token, user_id=None):
    online_friend_ids = vk_api.fetch_online_friend_ids(access_token, user_id)
    online_desktop_ids = online_friend_ids['online']
    online_mobile_ids = online_friend_ids['online_mobile']
    online_friends = []
    for online_id in online_desktop_ids + online_mobile_ids:
        # FIXME: employ a different approach
        user = vk_api.invoke_with_cooldown(vk_api.fetch_user, access_token=access_token, 
                                           username=online_id)
        name = ' '.join((user['first_name'], user['last_name']))
        online_friends.append({'name': name,
                               'url': 'https://vk.com/id%d' % online_id,
                               'mobile': online_id in online_mobile_ids})
    return online_friends
