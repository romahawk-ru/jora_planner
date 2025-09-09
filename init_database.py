from app import app, db
from models import User, Category, Tag, Task

def init_database():
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("Все таблицы созданы успешно!")
        
        # Проверяем соединение с БД
        try:
            db.session.execute('SELECT 1')
            print("Соединение с базой данных установлено")
        except Exception as e:
            print(f"Ошибка соединения: {e}")
            return False
            
        return True

if __name__ == '__main__':
    if init_database():
        print("База данных инициализирована успешно!")
    else:
        print("Ошибка инициализации базы данных")