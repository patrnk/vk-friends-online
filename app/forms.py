from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL
from .vk import vk_api

class UserUrlForm(FlaskForm):
    _validators = [DataRequired(message='Это обязательное поле.'), 
                   Length(min=1, max=50, 
                          message='Ссылка не должна быть длиннее 50 символов.'),
                   URL(message='Это не ссылка.'),
                   ]
    user_url = StringField('user_url', validators=_validators) 
