import sqlite3
import os
from app import app
from sqlalchemy import text  # Добавляем импорт

def check_database():
    print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")
    
    # Проверяем существование файла
    if os.path.exists('database.db'):
        print("✅ Файл database.db существует")
        file_size = os.path.getsize('database.db')
        print(f"📊 Размер файла: {file_size} байт")
    else:
        print("❌ Файл database.db не существует!")
        return False
    
    # Пробуем подключиться к базе через SQLAlchemy
    try:
        with app.app_context():
            # Проверяем соединение
            result = db.session.execute(text('SELECT 1')).scalar()
            print("✅ SQLAlchemy подключение успешно")
            
            # Получаем список таблиц через SQLAlchemy
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("📋 Таблицы в базе:")
            for table in tables:
                # Получаем количество записей в таблице
                count = db.session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                print(f"  {table}: {count} записей")
        
        print("✅ Проверка базы данных завершена успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе: {e}")
        return False

if __name__ == '__main__':
    with app.app_context():
        check_database()