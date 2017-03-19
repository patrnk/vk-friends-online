from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Length
from .vk import vk_api

class UserUrlForm(FlaskForm):
    _validators = [Length(min=0, max=50, 
                          message='Ссылка не должна быть длиннее 50 символов.'),
                   ]
    _placeholder = 'Твой профиль по умолчанию'
    user_url = StringField('user_url', validators=_validators, 
                           render_kw={'placeholder': _placeholder}) 
