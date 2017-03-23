import logging

from flask import request, redirect, url_for, session, escape, render_template
from app import app

from . import vk
from . import forms


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    params = {'logged_in': False,
              'welcome_text': 'Привет! Сначала нужно войти в ВК.',
              'auth_url': vk.form_authorization_url(request.url_root + 'callback'),
              'logout_url': url_for('logout'),
              'user_url_form': None,
              'online_friends': None,
              'target_name': None,
              }
    if 'username' not in session or 'access_token' not in session:
        return render_template('index.html', **params)

    params['logged_in'] = True
    params['welcome_text'] = 'Привет, %s!' % session['username']
    params['user_url_form'] = forms.UserUrlForm()
    access_token = escape(session['access_token'])

    if params['user_url_form'].validate_on_submit():
        target_url = params['user_url_form'].data['user_url']
        target_username = vk.extract_username_from_url(target_url)
        try:
            target = vk.fetch_user(access_token, target_username, name_case='gen')
            params['online_friends'] = vk.fetch_online_friends(access_token, target['id'])
        except vk.VkRequestError as ex:
            if ex.error_code == vk.ErrorCodes:
                return redirect(url_for('logout'))
            error_message = get_error_message(ex.error_code)
            if error_message is None:
                raise
            params['user_url_form'].user_url.errors.append(error_message)
            return render_template('index.html', **params)
        params['target_name'] = ' '.join((target['first_name'], target['last_name']))

    return render_template('index.html', **params)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code is None:
        return redirect(url_for('index'))
    redirect_uri = request.url_root + 'callback'  #VK insists it's the same as in index()
    try:
        access_token = vk.exchange_code_for_access_token(code, redirect_uri)
        first_name = vk.fetch_user(access_token)['first_name']
        session['access_token'] = access_token
        session['username'] = first_name
    except vk.VkRequestError:
        logger.warning('%s: %s', VkRequestError.message, VkRequestError.error_code)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('access_token', None)
    return redirect(url_for('index'))


def get_error_message(error_code):
    if (error_code == vk.ErrorCodes.TOO_MANY_REQUESTS or 
            error_code == vk.ErrorCodes.TOO_MANY_TYPICAL_REQUESTS):
        return 'Слишком много запросов. Подождите.'
    if error_code == vk.ErrorCodes.CAPTCHA_NEEDED:
        return 'ВКонтакте просит ввести капчу. Ничего не можем сделать.'
    if error_code == vk.ErrorCodes.USER_HAS_INVALID_ACCOUNT:
        return 'Зайдите на сайт и восстановите свой аккаунт.'
    if error_code == vk.ErrorCodes.NO_ACCESS:
        return 'У вас нет доступа к этой странице.'
    if error_code == vk.ErrorCodes.REQUESTED_USER_DELETED_OR_BANNED:
        return 'Эта страница удалена или заблокирована.'
    if error_code == vk.ErrorCodes.USERNAME_IS_INVALID:
        return 'Пользователя с таким юзернеймом не существует.'
