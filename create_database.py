from app import app, db
from models import User, Category, Tag, Task
from sqlalchemy import text  # Добавляем импорт

def create_database():
    with app.app_context():
        try:
            # Создаем все таблицы
            db.create_all()
            print("✓ Все таблицы базы данных созданы успешно!")
            
            # Проверяем соединение (исправленная версия)
            result = db.session.execute(text('SELECT 1')).scalar()
            print("✓ Соединение с базой данных установлено")
            
            # Проверяем существование таблиц
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✓ Таблицы в базе: {tables}")
            
            return True
            
        except Exception as e:
            print(f"✗ Ошибка создания базы данных: {e}")
            return False

if __name__ == '__main__':
    if create_database():
        print("\n✅ База данных успешно создана!")
    else:
        print("\n❌ Не удалось создать базу данных!")