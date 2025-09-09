from app import app, db
from models import User, Task, Category, Tag
from sqlalchemy import text
import os

def rebuild_database():
    print("=== ПОЛНОЕ ВОССТАНОВЛЕНИЕ БАЗЫ ДАННЫХ ===")
    
    # Удаляем старую базу если она есть
    if os.path.exists('database.db'):
        try:
            os.remove('database.db')
            print("🗑️ Старая база данных удалена")
        except Exception as e:
            print(f"❌ Ошибка удаления старой базы: {e}")
            return False
    
    with app.app_context():
        try:
            # Создаем новую базу
            db.create_all()
            print("✅ Новая база данных создана")
            
            # Проверяем соединение
            result = db.session.execute(text('SELECT 1')).scalar()
            print("✅ Соединение с БД установлено")
            
            # Создаем тестового пользователя
            user = User(username='admin', email='admin@example.com')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            print("✅ Тестовый пользователь создан")
            
            # Создаем тестовые категории и теги
            categories = [
                Category(name='Работа', color='#007bff', user_id=user.id),
                Category(name='Личное', color='#28a745', user_id=user.id),
                Category(name='Учеба', color='#dc3545', user_id=user.id)
            ]
            
            tags = [
                Tag(name='важно', user_id=user.id),
                Tag(name='срочно', user_id=user.id),
                Tag(name='проект', user_id=user.id)
            ]
            
            db.session.add_all(categories)
            db.session.add_all(tags)
            db.session.commit()
            print("✅ Тестовые данные созданы")
            
            # Проверяем что все создалось
            user_count = db.session.execute(text('SELECT COUNT(*) FROM user')).scalar()
            task_count = db.session.execute(text('SELECT COUNT(*) FROM task')).scalar()
            category_count = db.session.execute(text('SELECT COUNT(*) FROM category')).scalar()
            tag_count = db.session.execute(text('SELECT COUNT(*) FROM tag')).scalar()
            
            print(f"📊 Пользователей: {user_count}")
            print(f"📊 Задач: {task_count}")
            print(f"📊 Категорий: {category_count}")
            print(f"📊 Тегов: {tag_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при создании базы: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    if rebuild_database():
        print("\n🎉 База данных успешно восстановлена!")
        print("Теперь вы можете:")
        print("1. Запустить приложение: python app.py")
        print("2. Войти с логином: admin, паролем: admin123")
        print("3. Или зарегистрировать нового пользователя")
    else:
        print("\n😞 Не удалось восстановить базу данных")