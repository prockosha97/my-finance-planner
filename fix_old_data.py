import json
import datetime
import os

def fix_user_file(username):
    filename = f'user_data/{username}.json'
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Добавляем отсутствующие поля
        if 'start_date' not in data:
            data['start_date'] = datetime.date.today().isoformat()
        
        if 'end_date' not in data:
            data['end_date'] = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        
        if 'savings_percentage' not in data:
            data['savings_percentage'] = 15
        
        if 'show_all_days' not in data:
            data['show_all_days'] = False
        
        # Сохраняем исправленный файл
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Исправлен файл {username}.json")
        return True
    
    print(f"❌ Файл {username}.json не найден")
    return False

# Исправляем оба файла
fix_user_file('prockosha')
fix_user_file('Lesha_Petrov')