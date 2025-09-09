from app import app, db
from models import User, Category, Tag, Task

def recreate_database():
    with app.app_context():
        # Удаляем все таблицы
        db.drop_all()
        print("Все таблицы удалены")
        
        # Создаем все таблицы заново
        db.create_all()
        print("Все таблицы созданы заново")
        
        # Создаем тестового пользователя
        test_user = User(username='test', email='test@example.com')
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        print("Тестовый пользователь создан")
        
        # Создаем тестовые категории
        categories = [
            Category(name='Работа', color='#007bff', user_id=test_user.id),
            Category(name='Личное', color='#28a745', user_id=test_user.id),
            Category(name='Учеба', color='#dc3545', user_id=test_user.id)
        ]
        db.session.add_all(categories)
        
        # Создаем тестовые теги
        tags = [
            Tag(name='важно', user_id=test_user.id),
            Tag(name='срочно', user_id=test_user.id),
            Tag(name='проект', user_id=test_user.id)
        ]
        db.session.add_all(tags)
        
        db.session.commit()
        print("Тестовые данные созданы")
        
        return True

if __name__ == '__main__':
    if recreate_database():
        print("База данных пересоздана успешно!")
    else:
        print("Ошибка пересоздания базы данных")