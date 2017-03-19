from . import vk_api


def get_error_message(error_code):
    if (error_code == vk_api.ErrorCodes.TOO_MANY_REQUESTS or 
            error_code == vk_api.ErrorCodes.TOO_MANY_TYPICAL_REQUESTS):
        return 'Слишком много запросов. Подождите.'
    if error_code == vk_api.ErrorCodes.CAPTCHA_NEEDED:
        return 'ВКонтакте просит ввести капчу. Ничего не можем сделать.'
    if error_code == vk_api.ErrorCodes.USER_HAS_INVALID_ACCOUNT:
        return 'Зайдите на сайт и восстановите свой аккаунт.'
    if error_code == vk_api.ErrorCodes.NO_ACCESS:
        return 'У вас нет доступа к этой странице.'
    if error_code == vk_api.ErrorCodes.REQUESTED_USER_DELETED_OR_BANNED:
        return 'Эта страница удалена или заблокирована.'
    if error_code == vk_api.ErrorCodes.USERNAME_IS_INVALID:
        return 'Пользователя с таким юзернеймом не существует.'


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
    # VK API can't return more than 5k friend objects per query
    max_returned_number_of_friends = 5000
    friend_list = vk_api.fetch_friend_list(access_token, user_id)
    # VK doesn't allow its users to have more than 10k friends
    if len(friend_list) == max_returned_number_of_friends:
        friend_list += vk_api.fetch_friend_list(access_token, user_id,
                                                offset=max_returned_number_of_friends)
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
