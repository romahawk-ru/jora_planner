from app import app, db
from models import User, Category, Tag, Task
from sqlalchemy import text
import os

def force_create_db():
    print("=== ПРИНУДИТЕЛЬНОЕ СОЗДАНИЕ БАЗЫ ДАННЫХ ===")
    
    # Удаляем старую базу если она есть
    if os.path.exists('database.db'):
        try:
            os.remove('database.db')
            print("🗑️ Старая база данных удалена")
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
    
    try:
        with app.app_context():
            # Создаем все таблицы
            db.create_all()
            print("✅ Все таблицы созданы успешно!")
            
            # Проверяем соединение
            result = db.session.execute(text('SELECT 1')).scalar()
            print("✅ Соединение с БД установлено")
            
            # Проверяем таблицы
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Созданные таблицы: {tables}")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка создания базы: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if force_create_db():
        print("\n🎉 База данных успешно создана!")
        print("Теперь запустите: python app.py")
    else:
        print("\n❌ Не удалось создать базу данных")