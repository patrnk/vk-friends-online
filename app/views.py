from flask import request, redirect, url_for, session, escape
from app import app

from .vk import vk_api


@app.route('/')
@app.route('/index')
def index():
    url = vk_api.form_authorization_url(request.url_root + 'callback')
    username = 'Not logged in'
    if 'access_token' in session:
        access_token = escape(session['access_token'])
        try:
            username = vk_api.fetch_users_first_name(access_token)
        except vk_api.VkRequestError:
            session.pop('access_token')
    return '''
    <html>
        <head>
            <title> Hello! </title>
        </head>
        <body>
            <a href=''' + url + '''>Sign in VK</a>
            <p>''' + request.url_root + 'callback' + '''</p>
            <p>''' + username + '''</p>
        </body>
    </html>
    '''

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code is None:
        return redirect(url_for('index'))
    redirect_uri = request.url_root + 'callback'  #VK insists it's the same as in index()
    try:
        access_token = vk_api.exchange_code_for_access_token(code, redirect_uri)
        session['access_token'] = access_token
    except vk_api.VkRequestError:
        pass  #TODO: log the exception
    return redirect(url_for('index'))
