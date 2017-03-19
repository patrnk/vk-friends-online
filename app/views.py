from flask import request, redirect, url_for, session, escape, render_template
from app import app

from .vk import vk_api
from .vk import friends_online
from .forms import UserUrlForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    params = {'logged_in': False,
              'welcome_text': 'Привет! Сначала нужно войти в ВК.',
              'auth_url': vk_api.form_authorization_url(request.url_root + 'callback'),
              'user_url_form': None,
              'online_friends': None,
              'logout_url': url_for('logout')
              }
    if 'username' not in session or 'access_token' not in session:
        return render_template('index.html', **params)

    params['logged_in'] = True
    params['welcome_text'] = 'Привет, %s! Кого будем сталкерить?' % session['username']
    params['user_url_form'] = UserUrlForm()
    access_token = escape(session['access_token'])

    if params['user_url_form'].validate_on_submit():
        user_url = params['user_url_form'].data['user_url']
        user_id = friends_online.extract_user_id_from_url(user_url)
        params['online_friends'] = friends_online.fetch_online_friends(access_token, 
                                                                       user_id)

    return render_template('index.html', **params)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code is None:
        return redirect(url_for('index'))
    redirect_uri = request.url_root + 'callback'  #VK insists it's the same as in index()
    try:
        access_token = vk_api.exchange_code_for_access_token(code, redirect_uri)
        first_name = vk_api.fetch_user_name(access_token)[0]
        session['access_token'] = access_token
        session['username'] = first_name
    except vk_api.VkRequestError:
        pass  #TODO: log the exception
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('access_token', None)
    return redirect(url_for('index'))
