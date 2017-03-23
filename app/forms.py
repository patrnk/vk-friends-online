from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Length

class UserUrlForm(FlaskForm):
    _validators = [Length(min=0, max=50, 
                          message='Ссылка не должна быть длиннее 50 символов.'),
                   ]
    _placeholder = 'Твой профиль по умолчанию'
    user_url = StringField('user_url', validators=_validators, 
                           render_kw={'placeholder': _placeholder,
                                      'class': 'form_control col-md-6',
                                      'autofocus': 'True',
                                       }) 
