import json
import os
from datetime import datetime

class UserDataProcessor:
    """Класс для обработки данных пользователей"""
    
    def __init__(self, data_file):
        """
        Инициализация процессора данных
        
        Args:
            data_file (str): путь к файлу с данными
        """
        self.data_file = data_file
        self.users = []
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                print(f"Загружено {len(self.users)} пользователей")
            else:
                print("Файл данных не найден, создаем пустой список")
                self.users = []
        except json.JSONDecodeError as e:
            # FIXME: При поврежденном JSON файле теряются все данные
            # Нужно добавить создание резервной копии поврежденного файла
            print(f"Ошибка чтения JSON: {e}")
            self.users = []
    
    def add_user(self, name, email, age):
        """
        Добавление нового пользователя
        
        TODO: Добавить валидацию email
        TODO: Добавить проверку уникальности email
        """
        user = {
            'id': len(self.users) + 1,
            'name': name,
            'email': email,
            'age': age,
            'created_at': datetime.now().isoformat()
        }
        self.users.append(user)
        print(f"Пользователь {name} добавлен")
        
        # BUG: При большом количестве пользователей (>10000)
        # сохранение после каждого добавления работает медленно
        self.save_data()
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            print("Данные сохранены")
        except IOError as e:
            print(f"Ошибка сохранения: {e}")
    
    def get_user_by_id(self, user_id):
        """
        Поиск пользователя по ID
        
        TODO: Добавить кэширование результатов для частых запросов
        """
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
    
    def calculate_average_age(self):
        """
        Расчет среднего возраста пользователей
        
        FIXME: Функция падает с ZeroDivisionError при пустом списке пользователей
        Нужно добавить проверку на пустой список
        """
        total_age = sum(user['age'] for user in self.users)
        return total_age / len(self.users)
    
    def export_to_csv(self, filename):
        """
        Экспорт данных в CSV
        
        TODO: Добавить поддержку выбора полей для экспорта
        TODO: Добавить обработку специальных символов в полях
        """
        import csv
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if self.users:
                    fieldnames = self.users[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.users)
            print(f"Данные экспортированы в {filename}")
        except Exception as e:
            print(f"Ошибка экспорта: {e}")


def main():
    """Основная функция программы"""
    # TODO: Добавить обработку аргументов командной строки
    # TODO: Добавить интерактивный режим работы
    
    processor = UserDataProcessor("users.json")
    
    # Пример использования
    processor.add_user("Иван Петров", "ivan@example.com", 30)
    processor.add_user("Мария Иванова", "maria@example.com", 25)
    
    # FIXME: При сохранении кириллицы в JSON возникают проблемы с кодировкой
    # Временно решено через ensure_ascii=False
    
    avg_age = processor.calculate_average_age()
    print(f"Средний возраст: {avg_age}")


if __name__ == "__main__":
    main()