from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from models import db, User, Task, Category, Tag
from datetime import datetime, timedelta
from sqlalchemy import text
import os
from forms import LoginForm, RegistrationForm, TaskForm, EditTaskForm  # Убедитесь, что EditTaskForm добавлен

def translate_value(value, value_type):
    """Преобразует английские значения в русские для отображения"""
    translations = {
        'priority': {
            'low': 'Низкий',
            'medium': 'Средний',
            'high': 'Высокий'
        },
        'repeat': {
            'daily': 'Ежедневно',
            'weekly': 'Еженедельно',
            'monthly': 'Ежемесячно',
            'yearly': 'Ежегодно'
        }
    }
    
    return translations.get(value_type, {}).get(value, value)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_test_data():
    """Create test data if no users exist"""
    try:
        if User.query.count() == 0:
            print("Создаем тестового пользователя...")
            user = User(username='test', email='test@example.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
            print("✅ Тестовый пользователь создан")
            
            # Создаем тестовые категории
            categories = [
                Category(name='Работа', color='#007bff', user_id=user.id),
                Category(name='Личное', color='#28a745', user_id=user.id),
                Category(name='Учеба', color='#dc3545', user_id=user.id)
            ]
            
            # Создаем тестовые теги
            tags = [
                Tag(name='важно', user_id=user.id),
                Tag(name='срочно', user_id=user.id),
                Tag(name='проект', user_id=user.id)
            ]
            
            db.session.add_all(categories)
            db.session.add_all(tags)
            db.session.commit()
            print("✅ Тестовые категории и теги созданы")
            
    except Exception as e:
        print(f"Ошибка создания тестовых данных: {e}")
        db.session.rollback()

def init_database():
    """Initialize database tables"""
    try:
        with app.app_context():
            print("Инициализация базы данных...")
            
            # Создаем все таблицы
            db.create_all()
            print("✅ Таблицы базы данных созданы успешно!")
            
            # Проверяем соединение
            try:
                result = db.session.execute(text('SELECT 1')).scalar()
                print("✅ Соединение с БД установлено")
            except Exception as e:
                print(f"❌ Ошибка соединения: {e}")
                return False
                
            # Создаем тестовые данные
            create_test_data()
                
            return True
            
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        import traceback
        traceback.print_exc()
        return False

# Инициализируем базу данных при запуске
init_database()

@app.route('/')
@login_required
def index():
    return redirect(url_for('tasks'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            flash('Неверное имя пользователя или пароль', 'error')
        except Exception as e:
            flash('Ошибка при входе в систему', 'error')
            print(f"Login error: {e}")
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Имя пользователя уже занято', 'error')
                return render_template('register.html', form=form)
            
            if User.query.filter_by(email=form.email.data).first():
                flash('Email уже используется', 'error')
                return render_template('register.html', form=form)
            
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации. Попробуйте еще раз.', 'error')
            print(f"Registration error: {e}")
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

#Функция задача
@app.route('/tasks')
@login_required
def tasks():
    try:
        print(f"\n=== ЗАГРУЗКА ЗАДАЧ ДЛЯ ПОЛЬЗОВАТЕЛЯ {current_user.id} ===")
        
        # Получаем параметр фильтра из URL
        filter_type = request.args.get('filter', 'all')
        print(f"Фильтр: {filter_type}")
        
        # Базовый запрос для задач текущего пользователя
        query = Task.query.filter_by(user_id=current_user.id)
        
        # Применяем фильтры
        if filter_type == 'active':
            query = query.filter_by(completed=False)
            print("Фильтр: только активные задачи")
        elif filter_type == 'completed':
            query = query.filter_by(completed=True)
            print("Фильтр: только выполненные задачи")
        elif filter_type == 'overdue':
            # Просроченные задачи (не выполненные и с истекшим сроком)
            query = query.filter(
                Task.completed == False,
                Task.due_date < datetime.utcnow()
            )
            print("Фильтр: только просроченные задачи")
        
        # Получаем отфильтрованные задачи
        task_list = query.order_by(Task.created_at.desc()).all()
        
        # Добавляем русские отображаемые значения для каждой задачи
        for task in task_list:
            # Приоритет
            priority_translation = {
                'low': 'Низкий',
                'medium': 'Средний',
                'high': 'Высокий'
            }
            task.priority_display = priority_translation.get(task.priority, task.priority)
            
            # Повторение
            repeat_translation = {
                'daily': 'Ежедневно',
                'weekly': 'Еженедельно',
                'monthly': 'Ежемесячно',
                'yearly': 'Ежегодно'
            }
            if task.repeat_interval:
                task.repeat_interval_display = repeat_translation.get(task.repeat_interval, task.repeat_interval)
            else:
                task.repeat_interval_display = 'Не повторять'
        
        print(f"✅ Найдено задач после фильтра: {len(task_list)}")
        
        # Отладочная информация
        for i, task in enumerate(task_list, 1):
            status = "✓" if task.completed else "✗"
            overdue = "⚠" if task.is_overdue() else ""
            print(f"  {i}. [{status}{overdue}] '{task.title}' - Приоритет: {task.priority_display}")
        
        categories = Category.query.filter_by(user_id=current_user.id).all()
        tags = Tag.query.filter_by(user_id=current_user.id).all()
        
        # Получаем статистику по задачам
        total = Task.query.filter_by(user_id=current_user.id).count()
        active = Task.query.filter_by(user_id=current_user.id, completed=False).count()
        completed = Task.query.filter_by(user_id=current_user.id, completed=True).count()
        
        # Просроченные задачи
        overdue_count = Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == False,
            Task.due_date < datetime.utcnow()
        ).count()
        
        task_counts = {
            'total': total,
            'active': active,
            'completed': completed,
            'overdue': overdue_count
        }
        
        print(f"✅ Найдено категорий: {len(categories)}")
        print(f"✅ Найдено тегов: {len(tags)}")
        print("=== ЗАГРУЗКА ЗАВЕРШЕНА ===\n")
        
        # Check for reminders
        for task in task_list:
            if task.needs_reminder():
                flash(f'Напоминание: задача "{task.title}" требует внимания!', 'warning')
        
        return render_template('tasks.html', 
                            tasks=task_list, 
                            categories=categories, 
                            tags=tags, 
                            current_filter=filter_type,
                            task_counts=task_counts)
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в функции tasks(): {str(e)}")
        print(f"Тип ошибки: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        flash('Ошибка загрузки задач. Проверьте консоль для подробностей.', 'error')
        return render_template('tasks.html', 
                            tasks=[], 
                            categories=[], 
                            tags=[], 
                            current_filter='all',
                            task_counts={'total': 0, 'active': 0, 'completed': 0, 'overdue': 0})

#Функция добавить задачу
@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    
    try:
        # Создаем тестовые категории и теги если их нет
        if Category.query.filter_by(user_id=current_user.id).count() == 0:
            default_categories = [
                Category(name='Работа', color='#007bff', user_id=current_user.id),
                Category(name='Личное', color='#28a745', user_id=current_user.id),
                Category(name='Учеба', color='#dc3545', user_id=current_user.id)
            ]
            db.session.add_all(default_categories)
            db.session.commit()
        
        if Tag.query.filter_by(user_id=current_user.id).count() == 0:
            default_tags = [
                Tag(name='важно', user_id=current_user.id),
                Tag(name='срочно', user_id=current_user.id),
                Tag(name='проект', user_id=current_user.id)
            ]
            db.session.add_all(default_tags)
            db.session.commit()
        
        form.categories.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
        form.tags.choices = [(t.id, t.name) for t in Tag.query.filter_by(user_id=current_user.id).all()]
    except Exception as e:
        print(f"Error loading categories/tags: {e}")
        form.categories.choices = []
        form.tags.choices = []
    
    if form.validate_on_submit():
        try:
            print(f"Form data: {form.data}")
            
            task = Task(
                title=form.title.data,
                description=form.description.data,
                priority=form.priority.data,
                due_date=form.due_date.data,
                reminder_time=form.reminder_time.data,
                repeat_interval=form.repeat_interval.data if form.repeat_interval.data else None,
                user_id=current_user.id
            )
            
            # File attachment
            if form.attachment.data:
                file = form.attachment.data
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                task.attachment_path = file_path
                print(f"File saved: {file_path}")
            
            # Add categories
            if form.categories.data:
                print(f"Selected categories: {form.categories.data}")
                for category_id in form.categories.data:
                    category = Category.query.get(category_id)
                    if category and category.user_id == current_user.id:
                        task.categories.append(category)
                        print(f"Added category: {category.name}")
            
            # Add tags
            if form.tags.data:
                print(f"Selected tags: {form.tags.data}")
                for tag_id in form.tags.data:
                    tag = Tag.query.get(tag_id)
                    if tag and tag.user_id == current_user.id:
                        task.tags.append(tag)
                        print(f"Added tag: {tag.name}")
            
            db.session.add(task)
            db.session.commit()
            
            print(f"Task created successfully: {task.title}")
            flash('Задача добавлена успешно!', 'success')
            return redirect(url_for('tasks'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding task: {str(e)}")
            flash(f'Ошибка при добавлении задачи: {str(e)}', 'error')
    
    return render_template('add_task.html', form=form)

#Функция редактирования задачи
@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    try:
        # Получаем задачу или возвращаем 404
        task = Task.query.get_or_404(task_id)
        
        # Проверяем, что задача принадлежит текущему пользователю
        if task.user_id != current_user.id:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('tasks'))
        
        form = EditTaskForm()
        
        # Загружаем категории и теги пользователя
        form.categories.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
        form.tags.choices = [(t.id, t.name) for t in Tag.query.filter_by(user_id=current_user.id).all()]
        
        if form.validate_on_submit():
            try:
                # Обновляем основные поля
                task.title = form.title.data
                task.description = form.description.data
                task.priority = form.priority.data
                task.due_date = form.due_date.data
                task.reminder_time = form.reminder_time.data
                task.repeat_interval = form.repeat_interval.data if form.repeat_interval.data else None
                
                # Обработка удаления файла
                if form.delete_attachment.data and task.attachment_path:
                    if os.path.exists(task.attachment_path):
                        os.remove(task.attachment_path)
                    task.attachment_path = None
                
                # Обработка нового файла
                if form.attachment.data:
                    # Удаляем старый файл если есть
                    if task.attachment_path and os.path.exists(task.attachment_path):
                        os.remove(task.attachment_path)
                    
                    file = form.attachment.data
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    task.attachment_path = file_path
                
                # Обновляем категории
                task.categories.clear()
                for category_id in form.categories.data:
                    category = Category.query.get(category_id)
                    if category and category.user_id == current_user.id:
                        task.categories.append(category)
                
                # Обновляем теги
                task.tags.clear()
                for tag_id in form.tags.data:
                    tag = Tag.query.get(tag_id)
                    if tag and tag.user_id == current_user.id:
                        task.tags.append(tag)
                
                db.session.commit()
                flash('Задача успешно обновлена!', 'success')
                return redirect(url_for('tasks'))
                
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при обновлении задачи', 'error')
                print(f"Edit task error: {e}")
        
        else:
            # Заполняем форму текущими значениями задачи
            form.title.data = task.title
            form.description.data = task.description
            form.priority.data = task.priority
            form.due_date.data = task.due_date
            form.reminder_time.data = task.reminder_time
            form.repeat_interval.data = task.repeat_interval
            
            # Устанавливаем выбранные категории и теги
            form.categories.data = [c.id for c in task.categories]
            form.tags.data = [t.id for t in task.tags]
        
        return render_template('edit_task.html', form=form, task=task)
        
    except Exception as e:
        flash('Ошибка при загрузке формы редактирования', 'error')
        print(f"Edit task load error: {e}")
        return redirect(url_for('tasks'))

#Функция выполнения задачи
@app.route('/complete_task/<int:task_id>')
@login_required
def complete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        if task.user_id != current_user.id:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('tasks'))
        
        task.completed = not task.completed
        db.session.commit()
        
        if task.completed:
            flash('Задача отмечена как выполненная!', 'success')
        else:
            flash('Задача возвращена в активные!', 'info')
        
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при обновлении задачи', 'error')
        print(f"Complete task error: {e}")
    
    return redirect(url_for('tasks'))

@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        if task.user_id != current_user.id:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('tasks'))
        
        # Удаляем прикрепленный файл
        if task.attachment_path and os.path.exists(task.attachment_path):
            os.remove(task.attachment_path)
        
        db.session.delete(task)
        db.session.commit()
        flash('Задача удалена!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении задачи', 'error')
        print(f"Delete task error: {e}")
    
    return redirect(url_for('tasks'))

@app.route('/download_attachment/<int:task_id>')
@login_required
def download_attachment(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        if task.user_id != current_user.id:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('tasks'))
        
        if not task.attachment_path or not os.path.exists(task.attachment_path):
            flash('Файл не найден', 'error')
            return redirect(url_for('tasks'))
        
        return send_file(task.attachment_path, as_attachment=True)
        
    except Exception as e:
        flash('Ошибка при загрузке файла', 'error')
        print(f"Download attachment error: {e}")
        return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

def get_task_counts(user_id):
    """Получить количество задач по статусам"""
    try:
        total = Task.query.filter_by(user_id=user_id).count()
        active = Task.query.filter_by(user_id=user_id, completed=False).count()
        completed = Task.query.filter_by(user_id=user_id, completed=True).count()
        
        # Просроченные задачи
        overdue = Task.query.filter(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < datetime.utcnow()
        ).count()
        
        return {
            'total': total,
            'active': active,
            'completed': completed,
            'overdue': overdue
        }
    except Exception as e:
        print(f"Error getting task counts: {e}")
        return {'total': 0, 'active': 0, 'completed': 0, 'overdue': 0}