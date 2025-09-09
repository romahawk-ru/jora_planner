from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, PasswordField, SubmitField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Имя пользователя уже занято')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email уже используется')

class TaskForm(FlaskForm):
    title = StringField('Название задачи', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание')
    priority = SelectField('Приоритет', choices=[
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий')
    ], default='medium')
    due_date = DateTimeField('Срок выполнения', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    reminder_time = DateTimeField('Напоминание', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    repeat_interval = SelectField('Повторение', choices=[
        ('', 'Не повторять'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('yearly', 'Ежегодно')
    ], default='')
    categories = SelectMultipleField('Категории', coerce=int, validators=[Optional()])
    tags = SelectMultipleField('Теги', coerce=int, validators=[Optional()])
    attachment = FileField('Прикрепить файл', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'txt'], 'Только изображения и документы!')
    ])
    submit = SubmitField('Сохранить')

class EditTaskForm(FlaskForm):
    title = StringField('Название задачи', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание')
    priority = SelectField('Приоритет', choices=[
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий')
    ], default='medium')
    due_date = DateTimeField('Срок выполнения', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    reminder_time = DateTimeField('Напоминание', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    repeat_interval = SelectField('Повторение', choices=[
        ('', 'Не повторять'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('yearly', 'Ежегодно')
    ], default='')
    categories = SelectMultipleField('Категории', coerce=int, validators=[Optional()])
    tags = SelectMultipleField('Теги', coerce=int, validators=[Optional()])
    attachment = FileField('Прикрепить файл', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'txt'], 'Только изображения и документы!')
    ])
    delete_attachment = BooleanField('Удалить прикрепленный файл')
    submit = SubmitField('Обновить задачу')