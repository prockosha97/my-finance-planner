import streamlit as st
import datetime
import locale
from datetime import datetime as dt
import pandas as pd
import yaml
import json
import os
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# --- НАСТРОЙКА СТИЛЕЙ С МОБИЛЬНОЙ АДАПТАЦИЕЙ ---
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    pass

def format_currency(value):
    return f"{value:,.2f}".replace(',', ' ') if isinstance(value, (int, float)) else value

CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root {
    --primary: #4F46E5; --primary-light: #6366F1; --primary-dark: #3730A3; --secondary: #10B981; --danger: #EF4444; --warning: #F59E0B; --success: #10B981; --surface: #FFFFFF; --surface-light: #F9FAFB; --surface-dark: #F3F4F6; --border: #E5E7EB; --border-light: #F3F4F6; --text-primary: #111827; --text-secondary: #6B7280; --text-tertiary: #9CA3AF; --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05); --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08); --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08); --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px; --radius-xl: 20px;
}
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-tap-highlight-color: transparent;
}
body {
    background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%); color: var(--text-primary);
}
.stApp {
    background: transparent; max-width: 1400px !important; margin: 0 auto !important; padding: 0 12px !important;
}
.main .block-container {
    max-width: 1400px !important; padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 0.5rem !important; padding-bottom: 0.5rem !important;
}
.main-title {
    text-align: center; color: var(--text-primary); font-weight: 700; font-size: clamp(1.8rem, 5vw, 2.5rem); margin-bottom: 0.5rem; letter-spacing: -0.025em;
}
.subtitle {
    color: var(--text-secondary); text-align: center; font-weight: 400; font-size: clamp(0.9rem, 3vw, 1.1rem); margin-bottom: 1.5rem; line-height: 1.5; padding: 0 0.5rem;
}
.section-title {
    font-size: clamp(1.2rem, 4vw, 1.4rem); font-weight: 600; color: var(--text-primary); margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border-light);
}
.section-container {
    background: var(--surface); border-radius: var(--radius-xl); padding: 1.2rem; margin-bottom: 1.2rem; border: 1px solid var(--border); box-shadow: var(--shadow-sm); width: 100% !important;
}
.balance-card {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; border-radius: var(--radius-xl); padding: 1.5rem; text-align: center; margin: 1rem 0; position: relative; overflow: hidden;
}
.balance-label {
    font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-transform: uppercase;
}
.balance-value {
    font-size: clamp(2rem, 8vw, 2.8rem); font-weight: 700; margin: 0.5rem 0; letter-spacing: -0.025em;
}
.balance-subvalue {
    font-size: clamp(0.9rem, 3vw, 1.1rem); opacity: 0.9; margin-top: 0.5rem;
}

/* МОБИЛЬНЫЕ СТИЛИ ДЛЯ ВВОДА ДАННЫХ */
.mobile-input-group {
    display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1rem;
}
.mobile-input-row {
    display: flex; flex-direction: column; gap: 0.5rem; padding: 0.8rem; background: var(--surface-light); border-radius: var(--radius-md); border: 1px solid var(--border-light);
}
.mobile-income-item, .mobile-expense-item {
    display: flex; flex-direction: column; gap: 0.8rem; padding: 1rem; background: var(--surface-light); border-radius: var(--radius-lg); border: 1px solid var(--border); margin-bottom: 0.8rem;
}

/* АДАПТИВНЫЕ ТАБЛИЦЫ */
.compact-table-container {
    background: var(--surface); border-radius: var(--radius-lg); border: 1px solid var(--border-light); overflow: hidden; margin-top: 1rem; overflow-x: auto;
}
.table-header {
    display: grid; grid-template-columns: minmax(120px, 1fr) minmax(100px, 1fr) minmax(100px, 1fr) minmax(100px, 1fr) minmax(150px, 1fr); gap: 0.8rem; padding: 0.8rem; background: var(--surface-dark); border-bottom: 1px solid var(--border); font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); width: 100%; min-width: 600px;
}
.table-row {
    display: grid; grid-template-columns: minmax(120px, 1fr) minmax(100px, 1fr) minmax(100px, 1fr) minmax(100px, 1fr) minmax(150px, 1fr); gap: 0.8rem; padding: 0.8rem; border-bottom: 1px solid var(--border-light); align-items: center; width: 100%; min-width: 600px;
}
.table-row:hover {
    background: var(--surface-light);
}
.table-cell {
    min-width: 0; overflow: visible; white-space: normal; word-wrap: break-word; font-size: 0.9rem;
}

/* МОБИЛЬНАЯ ВЕРСИЯ ТАБЛИЦЫ ЕЖЕДНЕВНЫХ РАСХОДОВ */
.mobile-daily-table {
    display: flex; flex-direction: column; gap: 0.8rem;
}
.mobile-day-card {
    background: var(--surface); border-radius: var(--radius-lg); border: 1px solid var(--border-light); padding: 1rem; margin-bottom: 0.8rem;
}
.mobile-day-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-light);
}
.mobile-day-stats {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-bottom: 0.8rem;
}
.mobile-spend-item {
    display: flex; justify-content: space-between; align-items: center; padding: 0.6rem; background: var(--surface-light); border-radius: var(--radius-md); margin-bottom: 0.5rem;
}
.mobile-quick-input {
    display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.8rem;
}
.mobile-input-row-compact {
    display: flex; gap: 0.5rem; align-items: center;
}

/* АДАПТИВНЫЕ КНОПКИ И ИНПУТЫ */
.stButton > button {
    border-radius: var(--radius-md) !important; font-weight: 500 !important; font-size: 0.9rem !important; padding: 0.7rem 1rem !important; min-width: auto !important; white-space: nowrap !important; min-height: 44px !important; /* Для сенсорных экранов */
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    border-radius: var(--radius-md) !important; border: 1px solid var(--border) !important; padding: 0.8rem !important; font-size: 1rem !important; /* Больше для мобилок */ width: 100% !important; min-width: 0 !important; max-width: none !important; min-height: 44px !important;
}
.stSelectbox > div {
    min-width: 0 !important; max-width: none !important;
}
.stTextInput > div {
    min-width: 0 !important; max-width: none !important;
}
.stNumberInput > div {
    min-width: 0 !important; max-width: none !important;
}
[data-testid="stMetric"] {
    min-width: 0 !important; max-width: none !important; padding: 0.5rem !important;
}
[data-testid="stMetricValue"] {
    font-size: clamp(1.4rem, 5vw, 1.8rem) !important; font-weight: 700 !important; white-space: normal !important; overflow: visible !important; text-overflow: clip !important; max-width: none !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.9rem !important; white-space: normal !important; overflow: visible !important; text-overflow: clip !important; max-width: none !important;
}
[data-testid="stColumn"] > div {
    min-width: 0 !important; max-width: none !important;
}
.divider {
    height: 1px; background: var(--border-light); margin: 1rem 0;
}
.spend-bubble {
    background: var(--surface-dark); border-radius: var(--radius-md); padding: 0.6rem 0.8rem; margin: 0.25rem; display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; border: 1px solid var(--border-light); white-space: normal; max-width: 100%; overflow: hidden;
}
.mobile-spend-bubble {
    display: flex; justify-content: space-between; align-items: center; padding: 0.8rem; background: var(--surface-light); border-radius: var(--radius-md); margin-bottom: 0.5rem; border: 1px solid var(--border-light);
}

/* МЕДИА-ЗАПРОСЫ ДЛЯ РАЗНЫХ ЭКРАНОВ */
@media (max-width: 768px) {
    .stApp {
        padding: 0 8px !important;
    }
    .main .block-container {
        padding-left: 0.5rem !important; padding-right: 0.5rem !important;
    }
    .section-container {
        padding: 1rem;
    }
    .balance-card {
        padding: 1.2rem;
    }
    /* Скрываем десктопную таблицу, показываем мобильную */
    .compact-table-container {
        display: none;
    }
    .mobile-daily-table {
        display: flex;
    }
    /* Адаптивные колонки */
    [data-testid="column"] {
        width: 100% !important; margin-bottom: 1rem;
    }
    /* Улучшаем форму быстрого ввода */
    .mobile-quick-input .stTextInput input,
    .mobile-quick-input .stNumberInput input {
        font-size: 16px !important; /* Отключаем zoom в iOS */
    }
}

@media (min-width: 769px) {
    .mobile-daily-table {
        display: none;
    }
    .compact-table-container {
        display: block;
    }
}

/* ХОВЕР ЭФФЕКТЫ ТОЛЬКО ДЛЯ ДЕСКТОПА */
@media (hover: hover) and (pointer: fine) {
    .table-row:hover {
        background: var(--surface-light);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        transition: transform 0.2s;
    }
}

/* IOS SPECIFIC */
@supports (-webkit-touch-callout: none) {
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        font-size: 16px !important; /* Предотвращает zoom в iOS */
    }
}

/* АДАПТИВНЫЕ РАЗМЕРЫ ШРИФТОВ */
h1 { font-size: clamp(1.8rem, 5vw, 2.5rem) !important; }
h2 { font-size: clamp(1.4rem, 4vw, 1.8rem) !important; }
h3 { font-size: clamp(1.2rem, 3.5vw, 1.5rem) !important; }
p, span, div { font-size: clamp(0.9rem, 2.5vw, 1rem) !important; }

/* УЛУЧШАЕМ СЕНСОРНЫЕ ЭЛЕМЕНТЫ */
.touch-target {
    min-height: 44px; min-width: 44px;
}
input::placeholder,
textarea::placeholder {
    color: var(--text-tertiary) !important; opacity: 0.7 !important; font-size: 0.95rem !important;
}
"""
st.markdown(f"<style>{CSS_STYLE}</style>", unsafe_allow_html=True)

# --- КЛАСС ДЛЯ УПРАВЛЕНИЯ ДАННЫМИ ---
class UserDataManager:
    def __init__(self, username):
        self.username = username
        self.data_file = f'user_data/{username}.json'
        
    def load(self):
        """Загрузить все данные пользователя"""
        os.makedirs('user_data', exist_ok=True)
        
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                
            default_data = self.get_default_data()
            
            for key, default_value in default_data.items():
                if key not in loaded_data:
                    loaded_data[key] = default_value
            
            return loaded_data
        else:
            return self.get_default_data()
    
    def get_default_data(self):
        """Возвращает данные по умолчанию"""
        return {
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
            'incomes': [{"name": "Зарплата", "value": 50000.0, "category": "Основной"}],
            'expenses': [{"name": "Квартира", "value": 15000.0, "category": "Жилье"}],
            'daily_spends': {},
            'savings_percentage': 15,
            'categories': ["Основной", "Дополнительный", "Инвестиции", "Подарки", "Фриланс"],
            'expense_categories': ["Жилье", "Еда", "Транспорт", "Развлечения", "Здоровье", "Образование", "Покупки", "Прочее"],
            'show_all_days': False,
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def save(self, data):
        """Сохранить все данные пользователя"""
        data['last_updated'] = datetime.datetime.now().isoformat()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    
    def update_field(self, data, field_name, value):
        """Обновить одно поле и сохранить"""
        data[field_name] = value
        return self.save(data)
    
    @staticmethod
    def register_new_user(username, email, name, password):
        """Зарегистрировать нового пользователя"""
        config_file = 'config.yaml'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = yaml.load(f, Loader=SafeLoader)
            
            if username in config['credentials']['usernames']:
                return False, "Пользователь с таким логином уже существует"
        
        hashed_password = stauth.Hasher([password]).generate()[0]
        
        new_user = {
            'email': email,
            'name': name,
            'password': hashed_password
        }
        
        return True, new_user
    
    def save_new_user_to_config(self, new_user_data):
        """Сохранить нового пользователя в config.yaml"""
        config_file = 'config.yaml'
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = yaml.load(f, Loader=SafeLoader)
        else:
            config = {
                'credentials': {'usernames': {}},
                'cookie': {
                    'name': 'finance_app_cookie',
                    'key': 'your_random_key_here_123456789',
                    'expiry_days': 30
                },
                'preauthorized': {'emails': []}
            }
        
        config['credentials']['usernames'][self.username] = new_user_data
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return True

# --- ФОРМА РЕГИСТРАЦИИ ---
def show_registration_form():
    """Показать форму регистрации"""
    with st.container():
        st.markdown('<div class="section-title">📝 Регистрация нового пользователя</div>', unsafe_allow_html=True)
        
        with st.form(key="registration_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Логин*", placeholder="Придумайте логин", key="reg_username")
                new_email = st.text_input("Email*", placeholder="your@email.com", key="reg_email")
            
            with col2:
                new_name = st.text_input("Имя и фамилия*", placeholder="Иван Иванов", key="reg_name")
                new_password = st.text_input("Пароль*", type="password", placeholder="Не менее 6 символов", key="reg_pass")
                confirm_password = st.text_input("Подтвердите пароль*", type="password", key="reg_pass_confirm")
            
            st.markdown("**Обязательные поля отмечены *")
            
            col_submit, col_info = st.columns([1, 2])
            with col_submit:
                submitted = st.form_submit_button("Зарегистрироваться", use_container_width=True, type="primary", key="reg_submit")
            
            with col_info:
                st.info("""
                📝 После регистрации:
                - Вы сразу сможете войти в систему
                - Ваши данные будут сохранены отдельно
                - Вы сможете настроить свой финансовый план
                """)
            
            if submitted:
                if not all([new_username, new_email, new_name, new_password, confirm_password]):
                    st.error("❌ Заполните все обязательные поля!")
                    return False
                
                if new_password != confirm_password:
                    st.error("❌ Пароли не совпадают!")
                    return False
                
                if len(new_password) < 6:
                    st.error("❌ Пароль должен быть не менее 6 символов!")
                    return False
                
                user_manager = UserDataManager(new_username)
                success, result = user_manager.register_new_user(
                    new_username, new_email, new_name, new_password
                )
                
                if success:
                    user_manager.save_new_user_to_config(result)
                    user_data = user_manager.load()
                    user_manager.save(user_data)
                    
                    st.success(f"✅ Пользователь {new_username} успешно зарегистрирован!")
                    st.info("Теперь вы можете войти в систему со своим логином и паролем.")
                    return True
                else:
                    st.error(f"❌ {result}")
                    return False
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    return False

# --- ЗАГРУЗКА КОНФИГУРАЦИИ ---
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config.get('preauthorized', {})
    )
except Exception as e:
    st.error(f"Ошибка загрузки конфигурации: {str(e)}")
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.set_page_config(
    layout="wide",
    page_title="💰 Финансовый Планнер",
    page_icon="💸",
    initial_sidebar_state="collapsed"
)

# --- ВКЛАДКИ ВХОДА И РЕГИСТРАЦИИ ---
st.markdown('<div class="main-title">💰 Финансовый Планнер</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Управление бюджетом • Аналитика • Регистрация новых пользователей</div>', unsafe_allow_html=True)

# Инициализируем переменные
authentication_status = None
username = None
name = None

# Создаем вкладки
tab1, tab2 = st.tabs(["🔐 Вход в систему", "📝 Регистрация"])

with tab1:
    name, authentication_status, username = authenticator.login('Вход', 'main')
    
    if authentication_status is False:
        st.error("❌ Неверный логин или пароль")
    
    if authentication_status is None:
        st.info("Введите логин и пароль для входа")

with tab2:
    registration_success = show_registration_form()

# ПРОВЕРКА АВТОРИЗАЦИИ
if authentication_status is False:
    st.stop()

if authentication_status is None and not registration_success:
    st.warning("🔐 Пожалуйста, войдите или зарегистрируйтесь")
    st.stop()

# ЕСЛИ ПОЛЬЗОВАТЕЛЬ ЗАРЕГИСТРИРОВАЛСЯ - ПЕРЕЗАГРУЖАЕМ
if registration_success:
    st.rerun()

# --- ТЕПЕРЬ ОСНОВНОЕ ПРИЛОЖЕНИЕ (после авторизации) ---

# --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ ПОЛЬЗОВАТЕЛЯ ---
user_manager = UserDataManager(username)
user_key = f"user_{username}"

if user_key not in st.session_state:
    user_data = user_manager.load()
    st.session_state[user_key] = user_data
    st.session_state['current_user'] = username
elif st.session_state.get('current_user') != username:
    user_data = user_manager.load()
    st.session_state[user_key] = user_data
    st.session_state['current_user'] = username

user_data = st.session_state[user_key]

# --- ШАПКА С ИНФОРМАЦИЕЙ О ПОЛЬЗОВАТЕЛЕ ---
user_col1, user_col2, user_col3 = st.columns([2, 1, 1])
with user_col1:
    st.markdown(f'<div class="main-title">💰 Финансовый Планнер</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Простое управление бюджетом • Аналитика в реальном времени • Минималистичный дизайн</div>', unsafe_allow_html=True)

with user_col3:
    user_info = config['credentials']['usernames'].get(username, {})
    display_name = user_info.get('name', username)
    st.info(f"👤 {display_name}")
    authenticator.logout('Выйти', 'main')

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 1. ПЕРИОД РАСЧЕТА (АДАПТИВНЫЙ) ---
with st.container():
    st.markdown('<div class="section-title">📅 Период расчета</div>', unsafe_allow_html=True)
    
    # На мобилке - вертикальное расположение
    if st.session_state.get('is_mobile', False):
        saved_start = datetime.date.fromisoformat(user_data['start_date'])
        start_date = st.date_input(
            "Начало периода",
            saved_start,
            format="DD.MM.YYYY",
            key=f"start_date_{username}"
        )
        
        saved_end = datetime.date.fromisoformat(user_data['end_date'])
        end_date = st.date_input(
            "Конец периода",
            saved_end,
            format="DD.MM.YYYY",
            key=f"end_date_{username}"
        )
    else:
        # На десктопе - горизонтальное
        col1, col2, col3 = st.columns([1.2, 1.2, 0.8])
        
        with col1:
            saved_start = datetime.date.fromisoformat(user_data['start_date'])
            start_date = st.date_input(
                "Начало периода",
                saved_start,
                format="DD.MM.YYYY",
                key=f"start_date_{username}"
            )
        
        with col2:
            saved_end = datetime.date.fromisoformat(user_data['end_date'])
            end_date = st.date_input(
                "Конец периода",
                saved_end,
                format="DD.MM.YYYY",
                key=f"end_date_{username}"
            )
        
        with col3:
            days_in_period = max((end_date - start_date).days + 1, 1)
            st.metric(
                "Дней в периоде",
                days_in_period,
                f"{start_date.strftime('%d.%m')} - {end_date.strftime('%d.%m')}"
            )
    
    # Сохраняем изменения дат
    if 'start_date' in locals() and start_date != saved_start:
        user_data['start_date'] = start_date.isoformat()
        user_manager.save(user_data)
    
    if 'end_date' in locals() and end_date != saved_end:
        user_data['end_date'] = end_date.isoformat()
        user_manager.save(user_data)
    
    # Показываем метрику дней на мобилке отдельно
    if st.session_state.get('is_mobile', False) and 'start_date' in locals() and 'end_date' in locals():
        days_in_period = max((end_date - start_date).days + 1, 1)
        st.metric(
            "Дней в периоде",
            days_in_period,
            f"{start_date.strftime('%d.%m')} - {end_date.strftime('%d.%m')}"
        )
    
    if start_date > end_date:
        st.error("❌ Дата начала не может быть позже окончания.")
        st.stop()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 2. ДОХОДЫ И РАСХОДЫ (АДАПТИВНЫЕ) ---
# На мобилке показываем последовательно, на десктопе - колонками
if st.session_state.get('is_mobile', False):
    # МОБИЛЬНАЯ ВЕРСИЯ: доходы и расходы по очереди
    st.markdown('<div class="section-title">💸 Доходы</div>', unsafe_allow_html=True)
    total_income = 0
    
    for i, income in enumerate(user_data['incomes']):
        with st.container():
            st.markdown(f'<div class="mobile-income-item">', unsafe_allow_html=True)
            
            cols = st.columns([3, 1])
            with cols[0]:
                new_name = st.text_input(
                    "Название дохода",
                    value=income['name'],
                    key=f"in_name_mobile_{username}_{i}",
                    placeholder="Источник дохода"
                )
            
            with cols[1]:
                new_value = st.number_input(
                    "Сумма",
                    value=float(income['value']),
                    step=1000.0,
                    format="%.0f",
                    key=f"in_value_mobile_{username}_{i}",
                    placeholder="0 ₽"
                )
            
            new_category = st.selectbox(
                "Категория",
                user_data['categories'],
                index=user_data['categories'].index(income['category']) 
                if income['category'] in user_data['categories'] else 0,
                key=f"in_cat_mobile_{username}_{i}"
            )
            
            # Сохраняем изменения
            if new_name != income['name']:
                user_data['incomes'][i]['name'] = new_name
                user_manager.save(user_data)
            
            if new_value != income['value']:
                user_data['incomes'][i]['value'] = new_value
                user_manager.save(user_data)
            
            if new_category != income['category']:
                user_data['incomes'][i]['category'] = new_category
                user_manager.save(user_data)
            
            total_income += user_data['incomes'][i]['value'] or 0
            
            # Кнопка удаления
            if len(user_data['incomes']) > 1:
                if st.button("🗑 Удалить", key=f"remove_income_mobile_{username}_{i}", use_container_width=True):
                    user_data['incomes'].pop(i)
                    user_manager.save(user_data)
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Кнопка добавления дохода
    if st.button("+ Добавить доход", use_container_width=True, type="secondary", key=f"add_income_mobile_{username}"):
        user_data['incomes'].append({
            "name": "", "value": 0.0, 
            "category": user_data['categories'][0]
        })
        user_manager.save(user_data)
        st.rerun()
    
    st.metric("Итого доходов", f"{format_currency(total_income)} ₽")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Расходы на мобилке
    st.markdown('<div class="section-title">🧾 Расходы</div>', unsafe_allow_html=True)
    total_expenses = 0
    
    for i, expense in enumerate(user_data['expenses']):
        with st.container():
            st.markdown(f'<div class="mobile-expense-item">', unsafe_allow_html=True)
            
            cols = st.columns([3, 1])
            with cols[0]:
                new_name = st.text_input(
                    "Название расхода",
                    value=expense['name'],
                    key=f"ex_name_mobile_{username}_{i}",
                    placeholder="Статья расхода"
                )
            
            with cols[1]:
                new_value = st.number_input(
                    "Сумма",
                    value=float(expense['value']),
                    step=1000.0,
                    format="%.0f",
                    key=f"ex_value_mobile_{username}_{i}",
                    placeholder="0 ₽"
                )
            
            new_category = st.selectbox(
                "Категория",
                user_data['expense_categories'],
                index=user_data['expense_categories'].index(expense['category']) 
                if expense['category'] in user_data['expense_categories'] else 0,
                key=f"ex_cat_mobile_{username}_{i}"
            )
            
            # Сохраняем изменения
            if new_name != expense['name']:
                user_data['expenses'][i]['name'] = new_name
                user_manager.save(user_data)
            
            if new_value != expense['value']:
                user_data['expenses'][i]['value'] = new_value
                user_manager.save(user_data)
            
            if new_category != expense['category']:
                user_data['expenses'][i]['category'] = new_category
                user_manager.save(user_data)
            
            total_expenses += user_data['expenses'][i]['value'] or 0
            
            # Кнопка удаления
            if len(user_data['expenses']) > 1:
                if st.button("🗑 Удалить", key=f"remove_expense_mobile_{username}_{i}", use_container_width=True):
                    user_data['expenses'].pop(i)
                    user_manager.save(user_data)
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Кнопка добавления расхода
    if st.button("+ Добавить расход", use_container_width=True, type="secondary", key=f"add_expense_mobile_{username}"):
        user_data['expenses'].append({
            "name": "", "value": 0.0, 
            "category": user_data['expense_categories'][0]
        })
        user_manager.save(user_data)
        st.rerun()
    
    st.metric("Итого расходов", f"{format_currency(total_expenses)} ₽")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
else:
    # ДЕСКТОПНАЯ ВЕРСИЯ: две колонки
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="section-title">💸 Доходы</div>', unsafe_allow_html=True)
        total_income = 0
        
        for i, income in enumerate(user_data['incomes']):
            cols = st.columns([0.45, 0.25, 0.2, 0.1], gap="small")
            
            with cols[0]:
                new_name = st.text_input(
                    "Название дохода",
                    value=income['name'],
                    key=f"in_name_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="Источник дохода"
                )
                if new_name != income['name']:
                    user_data['incomes'][i]['name'] = new_name
                    user_manager.save(user_data)
            
            with cols[1]:
                new_value = st.number_input(
                    "Сумма",
                    value=float(income['value']),
                    step=1000.0,
                    format="%.0f",
                    key=f"in_value_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="0 ₽"
                )
                if new_value != income['value']:
                    user_data['incomes'][i]['value'] = new_value
                    user_manager.save(user_data)
            
            with cols[2]:
                new_category = st.selectbox(
                    "Категория",
                    user_data['categories'],
                    index=user_data['categories'].index(income['category']) 
                    if income['category'] in user_data['categories'] else 0,
                    key=f"in_cat_{username}_{i}",
                    label_visibility="collapsed"
                )
                if new_category != income['category']:
                    user_data['incomes'][i]['category'] = new_category
                    user_manager.save(user_data)
            
            with cols[3]:
                if len(user_data['incomes']) > 1:
                    if st.button("🗑", key=f"remove_income_{username}_{i}", 
                               help="Удалить доход", use_container_width=True):
                        user_data['incomes'].pop(i)
                        user_manager.save(user_data)
                        st.rerun()
            
            total_income += user_data['incomes'][i]['value'] or 0
        
        add_col, total_col = st.columns([0.7, 0.3])
        with add_col:
            if st.button("+ Добавить доход", use_container_width=True, 
                        type="secondary", key=f"add_income_{username}"):
                user_data['incomes'].append({
                    "name": "", "value": 0.0, 
                    "category": user_data['categories'][0]
                })
                user_manager.save(user_data)
                st.rerun()
        
        with total_col:
            st.metric("Итого доходов", f"{format_currency(total_income)} ₽")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title">🧾 Расходы</div>', unsafe_allow_html=True)
        total_expenses = 0
        
        for i, expense in enumerate(user_data['expenses']):
            cols = st.columns([0.45, 0.25, 0.2, 0.1], gap="small")
            
            with cols[0]:
                new_name = st.text_input(
                    "Название расхода",
                    value=expense['name'],
                    key=f"ex_name_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="Статья расхода"
                )
                if new_name != expense['name']:
                    user_data['expenses'][i]['name'] = new_name
                    user_manager.save(user_data)
            
            with cols[1]:
                new_value = st.number_input(
                    "Сумма",
                    value=float(expense['value']),
                    step=1000.0,
                    format="%.0f",
                    key=f"ex_value_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="0 ₽"
                )
                if new_value != expense['value']:
                    user_data['expenses'][i]['value'] = new_value
                    user_manager.save(user_data)
            
            with cols[2]:
                new_category = st.selectbox(
                    "Категория",
                    user_data['expense_categories'],
                    index=user_data['expense_categories'].index(expense['category']) 
                    if expense['category'] in user_data['expense_categories'] else 0,
                    key=f"ex_cat_{username}_{i}",
                    label_visibility="collapsed"
                )
                if new_category != expense['category']:
                    user_data['expenses'][i]['category'] = new_category
                    user_manager.save(user_data)
            
            with cols[3]:
                if len(user_data['expenses']) > 1:
                    if st.button("🗑", key=f"remove_expense_{username}_{i}", 
                               help="Удалить расход", use_container_width=True):
                        user_data['expenses'].pop(i)
                        user_manager.save(user_data)
                        st.rerun()
            
            total_expenses += user_data['expenses'][i]['value'] or 0
        
        add_col, total_col = st.columns([0.7, 0.3])
        with add_col:
            if st.button("+ Добавить расход", use_container_width=True, 
                        type="secondary", key=f"add_expense_{username}"):
                user_data['expenses'].append({
                    "name": "", "value": 0.0, 
                    "category": user_data['expense_categories'][0]
                })
                user_manager.save(user_data)
                st.rerun()
        
        with total_col:
            st.metric("Итого расходов", f"{format_currency(total_expenses)} ₽")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 3. БЮДЖЕТ И НАКОПЛЕНИЯ ---
balance_after_expenses = total_income - total_expenses

if balance_after_expenses >= 0:
    st.markdown('<div class="section-title">📊 Финансовый обзор</div>', unsafe_allow_html=True)
    
    # Адаптивные метрики
    if st.session_state.get('is_mobile', False):
        # На мобилке - вертикально
        st.metric("Общий доход", f"{format_currency(total_income)} ₽")
        st.metric("Общие расходы", f"{format_currency(total_expenses)} ₽")
        st.metric("Свободные средства", f"{format_currency(balance_after_expenses)} ₽")
    else:
        # На десктопе - горизонтально
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("Общий доход", f"{format_currency(total_income)} ₽")
        with metric_cols[1]:
            st.metric("Общие расходы", f"{format_currency(total_expenses)} ₽")
        with metric_cols[2]:
            st.metric("Свободные средства", f"{format_currency(balance_after_expenses)} ₽")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🏦 Планирование накоплений</div>', unsafe_allow_html=True)
    
    if st.session_state.get('is_mobile', False):
        # Мобильная версия: вертикально
        savings_percentage = st.slider(
            "Процент накоплений от свободных средств", 0, 100,
            user_data['savings_percentage'],
            format="%d%%", 
            key=f"savings_slider_mobile_{username}",
            help="Какую часть свободных средств откладывать"
        )
        
        savings_amount = balance_after_expenses * (savings_percentage / 100)
        disposable_income = balance_after_expenses - savings_amount
        daily_budget = disposable_income / days_in_period if days_in_period > 0 else 0
        
        st.markdown(f'''
        <div style="text-align: center; padding: 1rem; background: var(--surface-dark); border-radius: var(--radius-lg); border: 1px solid var(--border); margin: 1rem 0;">
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Отложу на накопления</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary); margin-bottom: 0.25rem;">{format_currency(savings_amount)} ₽</div>
            <div style="font-size: 0.85rem; color: var(--text-tertiary);">{savings_percentage}% от свободных средств</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if savings_percentage != user_data['savings_percentage']:
            user_data['savings_percentage'] = savings_percentage
            user_manager.save(user_data)
        
    else:
        # Десктопная версия
        col_slider, col_display = st.columns([2, 1])
        
        with col_slider:
            savings_percentage = st.slider(
                "Процент накоплений от свободных средств", 0, 100,
                user_data['savings_percentage'],
                format="%d%%", 
                key=f"savings_slider_{username}",
                help="Какую часть свободных средств откладывать"
            )
            if savings_percentage != user_data['savings_percentage']:
                user_data['savings_percentage'] = savings_percentage
                user_manager.save(user_data)
        
        savings_amount = balance_after_expenses * (savings_percentage / 100)
        disposable_income = balance_after_expenses - savings_amount
        daily_budget = disposable_income / days_in_period if days_in_period > 0 else 0
        
        with col_display:
            st.markdown(f'''
            <div style="text-align: center; padding: 1.2rem; background: var(--surface-dark); border-radius: var(--radius-lg); border: 1px solid var(--border); min-height: 120px;">
                <div style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Отложу на накопления</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: var(--primary); margin-bottom: 0.25rem;">{format_currency(savings_amount)} ₽</div>
                <div style="font-size: 0.9rem; color: var(--text-tertiary);">{savings_percentage}% от свободных средств</div>
            </div>
            ''', unsafe_allow_html=True)

    # Бюджетная карточка (одинаковая для всех устройств, но с адаптивными размерами)
    st.markdown(f'''
    <div class="balance-card">
        <div class="balance-label">БЮДЖЕТ НА ПЕРИОД</div>
        <div class="balance-value">{format_currency(disposable_income)} ₽</div>
        <div class="balance-subvalue">Доступно на {days_in_period} дней • {format_currency(daily_budget)} ₽ в день</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.error(f"⚠️ Дефицит бюджета: {format_currency(abs(balance_after_expenses))} ₽")
    st.warning("Рекомендуем увеличить доходы или уменьшить расходы")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 4. КОНТРОЛЬ РАСХОДОВ (ПОЛНОСТЬЮ ПЕРЕРАБОТАН ДЛЯ МОБИЛКИ) ---
if balance_after_expenses >= 0:
    st.markdown('<div class="section-title">📱 Контроль ежедневных расходов</div>', unsafe_allow_html=True)
    
    # БЫСТРЫЙ ВВОД ДЛЯ МОБИЛКИ
    with st.expander("💸 Быстрый ввод расхода", expanded=False):
        if st.session_state.get('is_mobile', False):
            # Мобильная версия быстрого ввода
            with st.form(key=f"quick_form_mobile_{username}", clear_on_submit=True):
                quick_desc = st.text_input("Что купили?", placeholder="Обед, кофе, бензин...", key=f"quick_desc_mobile_{username}")
                
                col_amount, col_cat = st.columns(2)
                with col_amount:
                    quick_amount = st.number_input("Сумма", min_value=0.0, step=100.0, format="%.0f", key=f"quick_amount_mobile_{username}", placeholder="0")
                with col_cat:
                    quick_category = st.selectbox("Категория", user_data['expense_categories'], key=f"quick_cat_mobile_{username}")
                
                if st.form_submit_button("💾 Добавить трату", use_container_width=True, type="primary"):
                    today_key = datetime.date.today().strftime("%Y-%m-%d")
                    if today_key not in user_data['daily_spends']:
                        user_data['daily_spends'][today_key] = []
                    if quick_desc and quick_amount > 0:
                        user_data['daily_spends'][today_key].append({
                            "desc": quick_desc, "amount": quick_amount, 
                            "category": quick_category, "time": dt.now().strftime("%H:%M")
                        })
                        user_manager.save(user_data)
                        st.success("✅ Трата добавлена!")
                        st.rerun()
        else:
            # Десктопная версия быстрого ввода
            cols = st.columns([0.4, 0.2, 0.25, 0.15])
            with cols[0]:
                quick_desc = st.text_input("Описание расхода", placeholder="Обед, кофе...", key=f"quick_desc_{username}")
            with cols[1]:
                quick_amount = st.number_input("Сумма", min_value=0.0, step=100.0, format="%.0f", key=f"quick_amount_{username}")
            with cols[2]:
                quick_category = st.selectbox("Категория", user_data['expense_categories'], key=f"quick_cat_{username}")
            with cols[3]:
                st.write("") 
                if st.button("➕ Добавить", use_container_width=True, type="primary", key=f"quick_add_{username}"):
                    today_key = datetime.date.today().strftime("%Y-%m-%d")
                    if today_key not in user_data['daily_spends']:
                        user_data['daily_spends'][today_key] = []
                    if quick_desc and quick_amount > 0:
                        user_data['daily_spends'][today_key].append({
                            "desc": quick_desc, "amount": quick_amount, 
                            "category": quick_category, "time": dt.now().strftime("%H:%M")
                        })
                        user_manager.save(user_data)
                        st.success("✅ Расход добавлен!")
                        st.rerun()
    
    # МОБИЛЬНАЯ ВЕРСИЯ ТАБЛИЦЫ (показывается только на мобилках)
    st.markdown('<div class="mobile-daily-table">', unsafe_allow_html=True)
    
    rollover = 0.0
    
    # Определяем сколько дней показывать
    if user_data['show_all_days']:
        display_days = days_in_period
    else:
        display_days = min(days_in_period, 5)  # На мобилке показываем меньше дней
    
    for i in range(display_days):
        current_day = start_date + datetime.timedelta(days=i)
        day_key = current_day.strftime("%Y-%m-%d")
        day_budget = daily_budget + rollover
        day_spends = user_data['daily_spends'].get(day_key, [])
        total_day_spend = sum(item['amount'] for item in day_spends)
        day_balance = day_budget - total_day_spend
        rollover = day_balance
        
        with st.container():
            st.markdown(f'<div class="mobile-day-card">', unsafe_allow_html=True)
            
            # Заголовок дня
            st.markdown(f'<div class="mobile-day-header">', unsafe_allow_html=True)
            col_date, col_balance = st.columns([2, 1])
            with col_date:
                st.markdown(f"**{current_day.strftime('%d %B')}**<br><span style='font-size:0.8rem; color: var(--text-secondary);'>{current_day.strftime('%A')}</span>", unsafe_allow_html=True)
            with col_balance:
                color = "var(--success)" if day_balance >= 0 else "var(--danger)"
                sign = "+" if day_balance >= 0 else ""
                st.markdown(f"<span style='color:{color}; font-weight:600;'>{sign}{format_currency(day_balance)} ₽</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Статистика дня
            st.markdown(f'<div class="mobile-day-stats">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Бюджет дня", f"{format_currency(day_budget)} ₽", delta=None)
            with col2:
                st.metric("Потрачено", f"{format_currency(total_day_spend)} ₽", delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Список трат
            if day_spends:
                st.markdown("**Траты:**")
                for j, spend in enumerate(day_spends):
                    st.markdown(f'''
                    <div class="mobile-spend-item">
                        <div>
                            <div style="font-weight: 500;">{spend["desc"]}</div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">
                                {spend["category"]} • {spend["time"]}
                            </div>
                        </div>
                        <div style="font-weight: 700; color: var(--primary);">
                            {format_currency(spend["amount"])} ₽
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Кнопка удаления рядом с каждой тратой
                    if st.button("×", key=f"del_mobile_{day_key}_{j}_{username}", help="Удалить"):
                        if day_key in user_data['daily_spends'] and j < len(user_data['daily_spends'][day_key]):
                            user_data['daily_spends'][day_key].pop(j)
                            user_manager.save(user_data)
                            st.rerun()
            
            # Быстрый ввод для этого дня
            st.markdown('<div class="mobile-quick-input">', unsafe_allow_html=True)
            with st.form(key=f"form_mobile_{day_key}_{username}", clear_on_submit=True):
                st.markdown(f'<div class="mobile-input-row-compact">', unsafe_allow_html=True)
                desc = st.text_input("", placeholder="Описание", key=f"desc_mobile_{day_key}_{username}", label_visibility="collapsed")
                amount = st.number_input("", min_value=0.0, step=100.0, format="%.0f", key=f"amount_mobile_{day_key}_{username}", label_visibility="collapsed", placeholder="0")
                if st.form_submit_button("➕", use_container_width=True, key=f"submit_mobile_{day_key}_{username}"):
                    if day_key not in user_data['daily_spends']:
                        user_data['daily_spends'][day_key] = []
                    if desc and amount > 0:
                        user_data['daily_spends'][day_key].append({
                            "desc": desc, "amount": amount, "category": "Прочее", "time": dt.now().strftime("%H:%M")
                        })
                        user_manager.save(user_data)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Кнопка показать все дни
    if not user_data['show_all_days'] and days_in_period > display_days:
        st.info(f"📅 Показано {display_days} из {days_in_period} дней.")
        if st.button(f"Показать все {days_in_period} дней", use_container_width=True, 
                    type="secondary", key=f"show_all_mobile_{username}"):
            user_data['show_all_days'] = True
            user_manager.save(user_data)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Закрываем mobile-daily-table
    
    # ДЕСКТОПНАЯ ВЕРСИЯ ТАБЛИЦЫ (скрыта на мобилках)
    st.markdown('<div class="compact-table-container">', unsafe_allow_html=True)
    
    rollover = 0.0
    header_cols = st.columns([1.8, 1.5, 1.5, 1.5, 2.5])
    header_cols[0].markdown("**Дата**")
    header_cols[1].markdown("**Бюджет дня**")
    header_cols[2].markdown("**Потрачено**")
    header_cols[3].markdown("**Остаток**")
    header_cols[4].markdown("**Быстрый ввод**")

    st.markdown('<hr style="margin: 0.5rem 0; border-color: var(--border-light);">', unsafe_allow_html=True)
    
    if user_data['show_all_days']:
        display_days = days_in_period
    else:
        display_days = min(days_in_period, 7)

    for i in range(display_days):
        current_day = start_date + datetime.timedelta(days=i)
        day_key = current_day.strftime("%Y-%m-%d")
        day_budget = daily_budget + rollover
        day_spends = user_data['daily_spends'].get(day_key, [])
        total_day_spend = sum(item['amount'] for item in day_spends)
        day_balance = day_budget - total_day_spend
        rollover = day_balance

        with st.container():
            row_cols = st.columns([1.8, 1.5, 1.5, 1.5, 2.5])
            with row_cols[0]:
                st.markdown(f"**{current_day.strftime('%d %B')}**<br><span style='font-size:0.85rem; color: var(--text-secondary);'>{current_day.strftime('%A')}</span>", unsafe_allow_html=True)
            with row_cols[1]:
                st.markdown(f"`{format_currency(day_budget)} ₽`")
            with row_cols[2]:
                st.markdown(f"`{format_currency(total_day_spend)} ₽`" if total_day_spend > 0 else "—", unsafe_allow_html=True)
            with row_cols[3]:
                color = "var(--success)" if day_balance >= 0 else "var(--danger)"
                sign = "+" if day_balance >= 0 else ""
                st.markdown(f"<span style='color:{color}; font-weight:500;'>{sign}{format_currency(day_balance)} ₽</span>", unsafe_allow_html=True)
            with row_cols[4]:
                with st.form(key=f"form_{day_key}_{username}", clear_on_submit=True):
                    form_cols = st.columns([0.5, 0.3, 0.2])
                    desc = form_cols[0].text_input("", placeholder="Описание", key=f"desc_{day_key}_{username}", label_visibility="collapsed")
                    amount = form_cols[1].number_input("", min_value=0.0, step=100.0, format="%.0f", key=f"amount_{day_key}_{username}", label_visibility="collapsed", placeholder="0")
                    if form_cols[2].form_submit_button("➕", use_container_width=True, key=f"submit_{day_key}_{username}"):
                        if day_key not in user_data['daily_spends']:
                            user_data['daily_spends'][day_key] = []
                        if desc and amount > 0:
                            user_data['daily_spends'][day_key].append({
                                "desc": desc, "amount": amount, "category": "Прочее", "time": dt.now().strftime("%H:%M")
                            })
                            user_manager.save(user_data)
                            st.rerun()

            if day_spends:
                st.markdown('<div style="margin-top: 0.5rem;">', unsafe_allow_html=True)
                for j, spend in enumerate(day_spends):
                    b_cols = st.columns([0.9, 0.1])
                    with b_cols[0]:
                         st.markdown(f'<div class="spend-bubble" title="{spend["desc"]}: {format_currency(spend["amount"])} ₽ ({spend["category"]})"><span>{spend["desc"]}: <b>{format_currency(spend["amount"])} ₽</b></span></div>', unsafe_allow_html=True)
                    with b_cols[1]:
                        if st.button("×", key=f"del_{day_key}_{j}_{username}", help="Удалить", use_container_width=True):
                            if day_key in user_data['daily_spends'] and j < len(user_data['daily_spends'][day_key]):
                                user_data['daily_spends'][day_key].pop(j)
                                user_manager.save(user_data)
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<hr style="margin: 0.5rem 0; border-color: var(--border-light);">', unsafe_allow_html=True)
    
    if not user_data['show_all_days'] and days_in_period > display_days:
        st.info(f"📅 Показано {display_days} из {days_in_period} дней.")
        if st.button(f"Показать все {days_in_period} дней", use_container_width=True, 
                    type="secondary", key=f"show_all_{username}"):
            user_data['show_all_days'] = True
            user_manager.save(user_data)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Закрываем compact-table-container

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 5. ЭКСПОРТ (АДАПТИВНЫЙ) ---
st.markdown('<div class="section-title">📤 Экспорт отчета</div>', unsafe_allow_html=True)
if balance_after_expenses >= 0:
    if st.session_state.get('is_mobile', False):
        # Мобильная версия экспорта
        col_stats, col_export = st.columns([1, 1])
        
        with col_stats:
            if user_data['daily_spends']:
                total_spent = sum(sum(item['amount'] for item in spends) for spends in user_data['daily_spends'].values())
                days_with_spends = len(user_data['daily_spends'])
                avg_daily_spent = total_spent / days_with_spends if days_with_spends > 0 else 0
                st.metric("Всего потрачено", f"{format_currency(total_spent)} ₽")
                st.metric("Средний расход", f"{format_currency(avg_daily_spent)} ₽")
            else:
                st.info("💡 Начните добавлять расходы, чтобы увидеть статистику")

        with col_export:
            user_info = config['credentials']['usernames'].get(username, {})
            report_text = f"""ФИНАНСОВЫЙ ОТЧЕТ
Пользователь: {user_info.get('name', username)}
Email: {user_info.get('email', '')}

Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
Дней в периоде: {days_in_period}

ДОХОДЫ:
Общий доход: {format_currency(total_income)} ₽

РАСХОДЫ:
Постоянные расходы: {format_currency(total_expenses)} ₽

НАКОПЛЕНИЯ:
Процент накоплений: {user_data['savings_percentage']}%
Сумма накоплений: {format_currency(savings_amount)} ₽

БЮДЖЕТ:
Доступно на период: {format_currency(disposable_income)} ₽
Бюджет на день: {format_currency(daily_budget)} ₽

Сгенерировано: {datetime.date.today().strftime('%d.%m.%Y')}
"""
            st.download_button(
                label="📄 Скачать отчет",
                data=report_text,
                file_name=f"отчет_{username}_{start_date.strftime('%Y-%m-%d')}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary",
                key=f"download_mobile_{username}"
            )
    else:
        # Десктопная версия экспорта
        col_stats, col_export = st.columns([1, 1])
        
        with col_stats:
            if user_data['daily_spends']:
                total_spent = sum(sum(item['amount'] for item in spends) for spends in user_data['daily_spends'].values())
                days_with_spends = len(user_data['daily_spends'])
                avg_daily_spent = total_spent / days_with_spends if days_with_spends > 0 else 0
                st.metric("Всего потрачено за период", f"{format_currency(total_spent)} ₽")
                st.metric("Средний расход в день", f"{format_currency(avg_daily_spent)} ₽")
            else:
                st.info("💡 Начните добавлять расходы, чтобы увидеть статистику")

        with col_export:
            user_info = config['credentials']['usernames'].get(username, {})
            report_text = f"""ФИНАНСОВЫЙ ОТЧЕТ
==================
Пользователь: {user_info.get('name', username)}
Email: {user_info.get('email', '')}

Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
Дней в периоде: {days_in_period}

ДОХОДЫ:
Общий доход: {format_currency(total_income)} ₽

РАСХОДЫ:
Постоянные расходы: {format_currency(total_expenses)} ₽

НАКОПЛЕНИЯ:
Процент накоплений: {user_data['savings_percentage']}%
Сумма накоплений: {format_currency(savings_amount)} ₽

БЮДЖЕТ:
Доступно на период: {format_currency(disposable_income)} ₽
Бюджет на день: {format_currency(daily_budget)} ₽

Сгенерировано: {datetime.date.today().strftime('%d.%m.%Y')}
"""
            st.download_button(
                label="📄 Скачать текстовый отчет",
                data=report_text,
                file_name=f"финансовый_отчет_{username}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary",
                key=f"download_{username}"
            )

# --- КНОПКА СОХРАНЕНИЯ ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
if st.button("💾 Сохранить все данные", use_container_width=True, key=f"save_all_{username}"):
    user_manager.save(user_data)
    st.success("✅ Все данные сохранены!")
    st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- ФУТЕР ---
st.markdown(f"""
<div style="text-align: center; color: var(--text-secondary); font-size: 0.9rem; padding: 1.5rem 0;">
    <div style="margin-bottom: 0.5rem;">
        <span style="margin: 0 0.5rem;">👤 Вы вошли как: {username}</span>
        <span style="margin: 0 0.5rem;">•</span>
        <span style="margin: 0 0.5rem;">💡 Все данные сохраняются автоматически</span>
    </div>
    <div>Финансовый Планнер • Версия 8.0 • 2024 • Полная мобильная поддержка</div>
</div>
""", unsafe_allow_html=True)

# --- ДЕТЕКТОР МОБИЛЬНОГО УСТРОЙСТВА ---
# Добавляем JavaScript для определения мобильного устройства
mobile_detector_js = """
<script>
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
           window.innerWidth <= 768;
}

if (isMobileDevice()) {
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: 'mobile'
    }, '*');
}
</script>
"""

st.components.v1.html(mobile_detector_js, height=0)

# Проверяем, было ли отправлено сообщение о мобильном устройстве
if 'is_mobile' not in st.session_state:
    st.session_state.is_mobile = False

# Можно также проверять ширину экрана через Streamlit
try:
    from streamlit_js_eval import streamlit_js_eval
    screen_width = streamlit_js_eval(js_expressions='screen.width', want_output=True)
    if screen_width and int(screen_width) <= 768:
        st.session_state.is_mobile = True
except:
    pass