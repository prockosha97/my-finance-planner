import json
import os

def save_user_data(username, data):
    """Сохранить данные пользователя"""
    os.makedirs('user_data', exist_ok=True)
    filename = f'user_data/{username}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_user_data(username):
    """Загрузить данные пользователя"""
    filename = f'user_data/{username}.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None