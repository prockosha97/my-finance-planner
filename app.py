import datetime
import json
import locale
import os
from datetime import datetime as dt
from io import BytesIO

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

try:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
except locale.Error:
    pass

st.set_page_config(
    layout="wide",
    page_title="💰 Финансовый Планнер",
    page_icon="💸",
    initial_sidebar_state="collapsed",
)


def format_currency(value):
    return f"{value:,.2f}".replace(",", " ") if isinstance(value, (int, float)) else value


CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #6366F1;
    --primary-dark: #4F46E5;
    --primary-soft: #E0E7FF;
    --secondary: #10B981;
    --danger: #EF4444;
    --danger-light: #FEE2E2;
    --success-light: #D1FAE5;
    --surface: #FFFFFF;
    --surface-light: #F8FAFC;
    --surface-dark: #F1F5F9;
    --border: #E2E8F0;
    --text-primary: #1E293B;
    --text-secondary: #64748B;
    --text-tertiary: #94A3B8;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 6px 14px rgba(15,23,42,0.08);
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    box-sizing: border-box;
}

.stApp {
    background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
    max-width: 1400px !important;
    margin: 0 auto !important;
}

.main .block-container {
    padding: 0.75rem 1rem 1.25rem !important;
    max-width: 1400px !important;
}

h1, h2, h3, h4, h5, h6, p, span, div {
    color: var(--text-primary);
    word-break: break-word;
    overflow-wrap: break-word;
}

h1 {
    font-size: clamp(1.6rem, 3.5vw, 2.4rem);
    line-height: 1.2;
}

h3 {
    font-size: clamp(1.1rem, 2.2vw, 1.6rem);
    line-height: 1.25;
}

.section-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 1rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
    width: 100%;
}

.section-title {
    font-size: clamp(1.1rem, 2vw, 1.35rem);
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.subtitle {
    color: var(--text-secondary);
    font-size: clamp(0.9rem, 1.6vw, 1rem);
    line-height: 1.45;
    white-space: normal;
}

.divider {
    height: 1px;
    background: var(--border);
    margin: 1rem 0;
}

.balance-card {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
    color: #FFFFFF;
    border-radius: var(--radius-xl);
    padding: 1.5rem;
    text-align: center;
    margin: 1.5rem 0;
    box-shadow: var(--shadow-md);
}

.balance-card .value {
    font-size: clamp(1.4rem, 3vw, 2rem);
    font-weight: 700;
    white-space: nowrap;
}

.balance-card .label,
.balance-card .subvalue {
    color: rgba(255, 255, 255, 0.85);
    white-space: nowrap;
}

/* Улучшенные поля ввода - ФИКС ДЛЯ МОБИЛЬНЫХ УСТРОЙСТВ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    min-height: 44px !important;
}

/* Исправление для темных тем на мобильных устройствах */
@media (prefers-color-scheme: dark) {
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-color: #E2E8F0 !important;
    }
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--primary-soft) !important;
}

/* УЛУЧШЕННЫЕ ВЫПАДАЮЩИЕ СПИСКИ - РАСШИРЕННЫЕ ДЛЯ КАТЕГОРИЙ */
div[data-baseweb="select"] {
    width: 100% !important;
    min-width: 180px !important;
}

div[data-baseweb="select"] > div {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    min-height: 44px !important;
    padding: 10px 12px !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: var(--primary) !important;
}

div[data-baseweb="select"] [role="listbox"] {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    max-height: 300px !important;
    overflow-y: auto !important;
    min-width: 250px !important;
    width: auto !important;
}

div[data-baseweb="select"] [role="option"] {
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    white-space: normal !important;
    word-break: break-word !important;
    padding: 12px 16px !important;
    min-height: 48px !important;
    display: flex !important;
    align-items: center !important;
}

div[data-baseweb="select"] [role="option"]:hover {
    background-color: var(--surface-dark) !important;
}

div[data-baseweb="select"] [data-testid="stSelectboxLabel"] {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Кнопки */
.stButton > button {
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

/* Компактный выбор даты */
.date-picker-container {
    margin-bottom: 1.5rem;
}

.date-picker-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    border: 1px solid var(--border);
    margin-bottom: 1rem;
}

.date-indicator {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-left: 8px;
}

.date-indicator.over-budget {
    background-color: var(--danger-light);
    color: var(--danger);
}

.date-indicator.within-budget {
    background-color: var(--success-light);
    color: var(--secondary);
}

/* Список трат */
.expense-list {
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.expense-item {
    background: var(--surface-light);
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.expense-item-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.expense-item-name {
    font-weight: 500;
    color: var(--text-primary);
}

.expense-item-amount {
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
}

.expense-item-time {
    font-size: 0.8rem;
    color: var(--text-tertiary);
    white-space: nowrap;
}

.expense-item-actions {
    display: flex;
    gap: 0.5rem;
}

/* Статистика дня */
.day-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-top: 1rem;
}

.stat-item {
    background: var(--surface-light);
    padding: 1rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    text-align: center;
}

.stat-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.stat-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stat-value.positive {
    color: var(--secondary);
}

.stat-value.negative {
    color: var(--danger);
}

.progress-bar {
    height: 8px;
    background: var(--surface-dark);
    border-radius: 4px;
    margin-top: 0.5rem;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.progress-fill.under {
    background: linear-gradient(90deg, var(--secondary), #34D399);
}

.progress-fill.over {
    background: linear-gradient(90deg, var(--danger), #F87171);
}

/* Форма ввода трат */
.expense-form-row {
    display: flex;
    gap: 0.75rem;
    align-items: end;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}

/* Улучшенные колонки для доходов/расходов */
.income-expense-row {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
}

.income-expense-row > div {
    flex: 1;
    min-width: 0;
}

/* Специальные стили для кнопок */
.login-button {
    background-color: var(--primary) !important;
    color: white !important;
    border: none !important;
}

.logout-button {
    background-color: #EF4444 !important;
    color: white !important;
    border: none !important;
}

.add-income-button, .add-expense-button {
    background-color: white !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
}

.add-income-button:hover, .add-expense-button:hover {
    background-color: var(--surface-dark) !important;
    border-color: var(--primary) !important;
}

.export-button {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
    color: white !important;
    border: none !important;
}

/* Адаптивность */
@media (max-width: 900px) {
    .main .block-container {
        padding: 1rem !important;
    }
    
    .section-card {
        padding: 1rem;
    }
    
    h1 {
        font-size: 1.8rem;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .subtitle {
        white-space: normal;
        word-break: break-word;
    }
    
    [data-testid="stHorizontalBlock"] {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    
    /* Улучшенные выпадающие списки для мобильных */
    div[data-baseweb="select"] > div {
        font-size: 16px !important;
        min-height: 48px !important;
        padding: 12px 14px !important;
    }
    
    div[data-baseweb="select"] [role="listbox"] {
        min-width: 100% !important;
        width: 100% !important;
    }
    
    div[data-baseweb="select"] [role="option"] {
        padding: 14px 16px !important;
        min-height: 52px !important;
    }
    
    /* Мобильные поля ввода */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        font-size: 16px !important;
        min-height: 48px !important;
    }
    
    /* Кнопки на мобилках */
    .stButton > button {
        min-height: 44px !important;
        font-size: 14px !important;
    }
    
    .expense-form-row {
        flex-direction: column;
        align-items: stretch;
        gap: 0.5rem;
    }
    
    .day-stats {
        grid-template-columns: 1fr;
        gap: 0.5rem;
    }
    
    .expense-item {
        padding: 0.5rem 0.75rem;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .expense-item-info {
        width: 100%;
        justify-content: space-between;
    }
    
    .expense-item-actions {
        width: 100%;
        justify-content: flex-end;
    }
    
    /* Улучшенные строки доходов/расходов на мобильных */
    .income-expense-row {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .income-expense-row > div {
        width: 100% !important;
    }
}

@media (max-width: 600px) {
    h1 {
        font-size: 1.6rem;
    }
    
    h3 {
        font-size: 1.2rem;
    }
    
    .stat-value {
        font-size: 1rem;
    }
    
    div[data-baseweb="select"] [role="option"] {
        font-size: 14px !important;
    }
}

/* Стили для форм аутентификации */
.auth-container {
    max-width: 500px;
    margin: 2rem auto;
    padding: 2rem;
}

.auth-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 2rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-md);
}

.auth-title {
    text-align: center;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
}
"""

st.markdown(f"<style>{CSS_STYLE}</style>", unsafe_allow_html=True)


class UserDataManager:
    def __init__(self, username):
        self.username = username
        self.data_file = f"user_data/{username}.json"

    def load(self):
        os.makedirs("user_data", exist_ok=True)
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            default_data = self.get_default_data()
            for key, default_value in default_data.items():
                if key not in loaded_data:
                    loaded_data[key] = default_value
            return loaded_data
        return self.get_default_data()

    def get_default_data(self):
        return {
            "start_date": datetime.date.today().isoformat(),
            "end_date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
            "incomes": [{"name": "Зарплата", "value": 50000.0, "category": "Основной"}],
            "expenses": [{"name": "Квартира", "value": 15000.0, "category": "Жилье"}],
            "daily_spends": {},
            "savings_percentage": 15,
            "categories": ["Основной", "Дополнительный", "Инвестиции", "Подарки", "Фриланс"],
            "expense_categories": [
                "Жилье",
                "Еда",
                "Транспорт",
                "Развлечения",
                "Здоровье",
                "Образование",
                "Покупки",
                "Прочее",
            ],
            "last_updated": datetime.datetime.now().isoformat(),
        }

    def save(self, data):
        data["last_updated"] = datetime.datetime.now().isoformat()
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True

    @staticmethod
    def register_new_user(username, email, name, password):
        config_file = "config.yaml"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = yaml.load(f, Loader=SafeLoader)
            if username in config["credentials"]["usernames"]:
                return False, "Пользователь с таким логином уже существует"

        hashed_password = stauth.Hasher([password]).generate()[0]
        new_user = {"email": email, "name": name, "password": hashed_password}
        return True, new_user

    def save_new_user_to_config(self, new_user_data):
        config_file = "config.yaml"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = yaml.load(f, Loader=SafeLoader)
        else:
            config = {
                "credentials": {"usernames": {}},
                "cookie": {
                    "name": "finance_app_cookie",
                    "key": "your_random_key_here_123456789",
                    "expiry_days": 30,
                },
                "preauthorized": {"emails": []},
            }

        config["credentials"]["usernames"][self.username] = new_user_data
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        return True


# Создаем конфиг если его нет
def ensure_config_exists():
    config_file = "config.yaml"
    if not os.path.exists(config_file):
        config = {
            "credentials": {"usernames": {}},
            "cookie": {
                "name": "finance_app_cookie",
                "key": "your_random_key_here_123456789",
                "expiry_days": 30,
            },
            "preauthorized": {"emails": []},
        }
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)


ensure_config_exists()

try:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # Создаем аутентификатор
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config.get("preauthorized", {}),
    )
except Exception as exc:
    st.error(f"Ошибка загрузки конфигурации: {exc}")
    st.stop()


def show_registration_form():
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("<h2 class='auth-title'>📝 Регистрация</h2>", unsafe_allow_html=True)
    
    with st.form(key="registration_form", clear_on_submit=True):
        new_username = st.text_input("Логин*", placeholder="Придумайте логин")
        new_email = st.text_input("Email*", placeholder="your@email.com")
        new_name = st.text_input("Имя и фамилия*", placeholder="Иван Иванов")
        
        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input("Пароль*", type="password")
        with col2:
            confirm_password = st.text_input("Подтвердите пароль*", type="password")

        submitted = st.form_submit_button("Зарегистрироваться", use_container_width=True, type="primary")
        if not submitted:
            st.markdown("</div>", unsafe_allow_html=True)
            return False

        if not all([new_username, new_email, new_name, new_password, confirm_password]):
            st.error("❌ Заполните все обязательные поля")
            st.markdown("</div>", unsafe_allow_html=True)
            return False

        if new_password != confirm_password:
            st.error("❌ Пароли не совпадают")
            st.markdown("</div>", unsafe_allow_html=True)
            return False

        if len(new_password) < 6:
            st.error("❌ Пароль должен быть не менее 6 символов")
            st.markdown("</div>", unsafe_allow_html=True)
            return False

        user_manager = UserDataManager(new_username)
        success, result = user_manager.register_new_user(new_username, new_email, new_name, new_password)

        if success:
            user_manager.save_new_user_to_config(result)
            user_data = user_manager.load()
            user_manager.save(user_data)
            st.success(f"✅ Пользователь {new_username} успешно зарегистрирован")
            st.info("Теперь вы можете войти в систему")
            st.markdown("</div>", unsafe_allow_html=True)
            return True

        st.error(f"❌ {result}")
        st.markdown("</div>", unsafe_allow_html=True)
        return False


def create_simple_export(user_data, username, user_info, start_date, end_date, 
                         total_income, total_expenses, disposable_income, daily_budget, days_in_period):
    """Создаёт простой текстовый файл с шаблоном"""
    
    report_text = f"""ФИНАНСОВЫЙ ШАБЛОН
========================
Пользователь: {user_info.get('name', username)}
Email: {user_info.get('email', '')}

Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
Дней в периоде: {days_in_period}

ОСНОВНЫЕ ПОКАЗАТЕЛИ:
-------------------
Общий доход: {format_currency(total_income)} ₽
Постоянные расходы: {format_currency(total_expenses)} ₽
Свободные средства: {format_currency(total_income - total_expenses)} ₽
Бюджет на период: {format_currency(disposable_income)} ₽
Бюджет на день: {format_currency(daily_budget)} ₽

ПОСТОЯННЫЕ ДОХОДЫ:
-----------------"""
    
    for income in user_data["incomes"]:
        report_text += f"\n• {income['name']}: {format_currency(income['value'])} ₽ ({income['category']})"
    
    report_text += "\n\nПОСТОЯННЫЕ РАСХОДЫ:\n-----------------"
    
    for expense in user_data["expenses"]:
        report_text += f"\n• {expense['name']}: {format_currency(expense['value'])} ₽ ({expense['category']})"
    
    report_text += "\n\nЕЖЕДНЕВНЫЕ ТРАТЫ (ШАБЛОН):\n-------------------------"
    report_text += "\nДата | Трата 1 | Трата 2 | Трата 3 | Трата 4 | Трата 5 | Итого | Остаток"
    report_text += "\n" + "-" * 80
    
    for i in range(days_in_period):
        current_date = start_date + datetime.timedelta(days=i)
        report_text += f"\n{current_date.strftime('%d.%m.%Y')} | | | | | | |"
    
    report_text += f"\n\nПОДСКАЗКИ:\n----------"
    report_text += "\n1. Заполняйте траты ежедневно"
    report_text += "\n2. Первые 5 колонок - для самых крупных трат дня"
    report_text += "\n3. Итого = сумма трат 1-5"
    report_text += "\n4. Остаток = Бюджет дня - Итого"
    report_text += "\n5. Красный цвет в приложении - перерасход бюджета"
    report_text += "\n6. Зелёный цвет - экономия"
    
    report_text += f"\n\nСгенерировано: {datetime.date.today().strftime('%d.%m.%Y %H:%M')}"
    
    return report_text


def get_day_status(day_key, user_data, daily_budget, start_date, end_date):
    """Определяет статус дня (перерасход/экономия)"""
    if day_key not in user_data["daily_spends"]:
        return None
    
    # Рассчитываем накопленный бюджет с переносом
    rollover = 0.0
    days_in_period = (end_date - start_date).days + 1
    
    for i in range(days_in_period):
        current_date = start_date + datetime.timedelta(days=i)
        current_key = current_date.isoformat()
        day_spent = sum(item["amount"] for item in user_data["daily_spends"].get(current_key, []))
        day_budget = daily_budget + rollover
        
        if current_key == day_key:
            if day_spent > day_budget and day_spent > 0:
                return "over"
            elif day_spent <= day_budget and day_spent > 0:
                return "within"
            return None
        
        rollover = max(day_budget - day_spent, 0)
    
    return None


def render_date_picker(start_date, end_date, selected_day, user_data, daily_budget):
    """Рендерит компактный выбор даты с индикаторами"""
    
    st.markdown("<div class='date-picker-card'>", unsafe_allow_html=True)
    st.markdown("### Выберите день для управления расходами")
    
    # Используем st.date_input для выбора даты
    new_date = st.date_input(
        "Дата",
        value=selected_day,
        min_value=start_date,
        max_value=end_date,
        format="DD.MM.YYYY",
        label_visibility="collapsed"
    )
    
    # Проверяем статус дня
    day_key = new_date.isoformat()
    day_status = get_day_status(day_key, user_data, daily_budget, start_date, end_date)
    
    # Индикатор статуса дня
    if day_status:
        status_text = "Перерасход" if day_status == "over" else "В пределах бюджета"
        status_class = "over-budget" if day_status == "over" else "within-budget"
        st.markdown(
            f"<span class='date-indicator {status_class}'>{status_text}</span>",
            unsafe_allow_html=True
        )
    
    # Информация о дне
    spends_today = user_data["daily_spends"].get(day_key, [])
    total_spent = sum(item["amount"] for item in spends_today)
    
    st.caption(f"📊 За этот день: {len(spends_today)} трат на {format_currency(total_spent)} ₽")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return new_date


# ================== НАЧАЛО ОСНОВНОГО ПРИЛОЖЕНИЯ ==================

# Инициализация session state
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False
if 'selected_day' not in st.session_state:
    st.session_state.selected_day = datetime.date.today()
if 'expense_page' not in st.session_state:
    st.session_state.expense_page = 0

# Проверяем аутентификацию ДО отображения контента
if st.session_state.get("authentication_status") is None:
    # Показываем только форму входа/регистрации
    st.markdown("<h1 style='text-align: center; margin-top: 2rem;'>💰 Финансовый Планнер</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: var(--text-secondary); margin-bottom: 2rem;'>Контроль бюджета, ежедневные траты и понятная аналитика.</p>", unsafe_allow_html=True)
    
    # Создаем две колонки для входа и регистрации
    auth_col1, auth_col2 = st.columns(2)
    
    with auth_col1:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown("<h2 class='auth-title'>🔐 Вход</h2>", unsafe_allow_html=True)
        
        try:
            # Пытаемся использовать стандартный authenticator
            name, authentication_status, username = authenticator.login(
                fields={'form_name': 'Вход', 
                       'username': 'Логин', 
                       'password': 'Пароль',
                       'login': 'Войти'}
            )
            
            if authentication_status:
                st.session_state["authentication_status"] = True
                st.session_state["username"] = username
                st.session_state["name"] = name
                st.rerun()
        except Exception as e:
            # Резервный метод входа
            with st.form(key="manual_login"):
                manual_username = st.text_input("Логин")
                manual_password = st.text_input("Пароль", type="password")
                login_submitted = st.form_submit_button("Войти", type="primary", use_container_width=True)
                
                if login_submitted:
                    if manual_username in config["credentials"]["usernames"]:
                        user_info = config["credentials"]["usernames"][manual_username]
                        st.session_state["authentication_status"] = True
                        st.session_state["username"] = manual_username
                        st.session_state["name"] = user_info["name"]
                        st.rerun()
                    else:
                        st.error("❌ Неверный логин или пароль")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with auth_col2:
        if show_registration_form():
            st.session_state.registration_success = True
            st.rerun()
    
    st.stop()

# Если регистрация успешна, просим войти
if st.session_state.registration_success:
    st.success("✅ Регистрация успешна! Теперь войдите в систему.")
    st.session_state.registration_success = False
    st.stop()

# Проверяем, что пользователь действительно аутентифицирован
username = st.session_state.get("username")
if not username:
    st.warning("🔐 Пожалуйста, войдите в систему снова")
    st.stop()

# ================== ОСНОВНОЙ КОНТЕНТ (после аутентификации) ==================

# Основной заголовок
st.markdown("<h1>💰 Финансовый Планнер</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Контроль бюджета, ежедневные траты и понятная аналитика.</div>",
    unsafe_allow_html=True,
)

# Загрузка данных пользователя
user_manager = UserDataManager(username)
user_key = f"user_{username}"

if user_key not in st.session_state:
    user_data = user_manager.load()
    st.session_state[user_key] = user_data
    st.session_state["current_user"] = username
elif st.session_state.get("current_user") != username:
    user_data = user_manager.load()
    st.session_state[user_key] = user_data
    st.session_state["current_user"] = username

user_data = st.session_state[user_key]

# Шапка пользователя
user_cols = st.columns([3, 1])
with user_cols[0]:
    user_info = config["credentials"]["usernames"].get(username, {})
    display_name = user_info.get("name", username)
    st.markdown(f"<h3>Здравствуйте, {display_name} 👋</h3>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Настройте период, доходы и ежедневные расходы.</div>",
        unsafe_allow_html=True,
    )
with user_cols[1]:
    if st.button("Выйти", type="primary", use_container_width=True, key="logout_btn"):
        authenticator.logout("Выйти", "main")
        st.session_state.clear()
        st.rerun()

# Период расчета
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📅 Период расчета</div>", unsafe_allow_html=True)
period_cols = st.columns([1.2, 1.2, 0.8])
with period_cols[0]:
    saved_start = datetime.date.fromisoformat(user_data["start_date"])
    start_date = st.date_input("Начало периода", saved_start, format="DD.MM.YYYY")
with period_cols[1]:
    saved_end = datetime.date.fromisoformat(user_data["end_date"])
    end_date = st.date_input("Конец периода", saved_end, format="DD.MM.YYYY")
with period_cols[2]:
    days_in_period = max((end_date - start_date).days + 1, 1)
    st.metric("Дней", days_in_period, f"{start_date.strftime('%d.%m')} - {end_date.strftime('%d.%m')}")

if start_date > end_date:
    st.error("❌ Дата начала не может быть позже окончания")
    st.stop()

if start_date != saved_start:
    user_data["start_date"] = start_date.isoformat()
    user_manager.save(user_data)

if end_date != saved_end:
    user_data["end_date"] = end_date.isoformat()
    user_manager.save(user_data)

st.markdown("</div>", unsafe_allow_html=True)

# Доходы и расходы
income_expense_cols = st.columns(2)

with income_expense_cols[0]:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💸 Доходы</div>", unsafe_allow_html=True)
    total_income = 0.0
    
    for i, income in enumerate(user_data["incomes"]):
        with st.container():
            # Улучшенная строка с увеличенными полями для категорий
            st.markdown("<div class='income-expense-row'>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([2.5, 1.8, 2.5, 0.4])
            
            with col1:
                new_name = st.text_input(
                    "Название дохода",
                    value=income["name"],
                    key=f"income_name_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="Название"
                )
            
            with col2:
                new_value = st.number_input(
                    "Сумма",
                    value=float(income["value"]),
                    step=1000.0,
                    format="%.0f",
                    key=f"income_value_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="Сумма"
                )
            
            with col3:
                # Улучшенный selectbox с расширенной шириной
                new_category = st.selectbox(
                    "Категория",
                    user_data["categories"],
                    index=user_data["categories"].index(income["category"])
                    if income["category"] in user_data["categories"]
                    else 0,
                    key=f"income_cat_{username}_{i}",
                    label_visibility="collapsed",
                    help="Выберите категорию дохода"
                )
            
            with col4:
                if len(user_data["incomes"]) > 1:
                    if st.button("🗑", key=f"income_remove_{username}_{i}"):
                        user_data["incomes"].pop(i)
                        user_manager.save(user_data)
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Сохранение изменений
            if new_name != income["name"]:
                user_data["incomes"][i]["name"] = new_name
                user_manager.save(user_data)
            if new_value != income["value"]:
                user_data["incomes"][i]["value"] = new_value
                user_manager.save(user_data)
            if new_category != income["category"]:
                user_data["incomes"][i]["category"] = new_category
                user_manager.save(user_data)

        total_income += user_data["incomes"][i]["value"] or 0

    # Кнопка добавления и итог
    add_col, total_col = st.columns([0.6, 0.4])
    with add_col:
        if st.button("+ Добавить доход", use_container_width=True, key=f"add_income_{username}", 
                    type="secondary"):
            user_data["incomes"].append({"name": "", "value": 0.0, "category": user_data["categories"][0]})
            user_manager.save(user_data)
            st.rerun()
    with total_col:
        st.metric("Итого", f"{format_currency(total_income)} ₽", label_visibility="collapsed")
    
    st.markdown("</div>", unsafe_allow_html=True)

with income_expense_cols[1]:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🧾 Расходы</div>", unsafe_allow_html=True)
    total_expenses = 0.0
    
    for i, expense in enumerate(user_data["expenses"]):
        with st.container():
            # Улучшенная строка с увеличенными полями для категорий
            st.markdown("<div class='income-expense-row'>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([2.5, 1.8, 2.5, 0.4])
            
            with col1:
                new_name = st.text_input(
                    "Название расхода",
                    value=expense["name"],
                    key=f"expense_name_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="Название"
                )
            
            with col2:
                new_value = st.number_input(
                    "Сумма",
                    value=float(expense["value"]),
                    step=500.0,
                    format="%.0f",
                    key=f"expense_value_{username}_{i}",
                    label_visibility="collapsed",
                    placeholder="Сумма"
                )
            
            with col3:
                # Улучшенный selectbox с расширенной шириной
                new_category = st.selectbox(
                    "Категория",
                    user_data["expense_categories"],
                    index=user_data["expense_categories"].index(expense["category"])
                    if expense["category"] in user_data["expense_categories"]
                    else 0,
                    key=f"expense_cat_{username}_{i}",
                    label_visibility="collapsed",
                    help="Выберите категорию расхода"
                )
            
            with col4:
                if len(user_data["expenses"]) > 1:
                    if st.button("🗑", key=f"expense_remove_{username}_{i}"):
                        user_data["expenses"].pop(i)
                        user_manager.save(user_data)
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Сохранение изменений
            if new_name != expense["name"]:
                user_data["expenses"][i]["name"] = new_name
                user_manager.save(user_data)
            if new_value != expense["value"]:
                user_data["expenses"][i]["value"] = new_value
                user_manager.save(user_data)
            if new_category != expense["category"]:
                user_data["expenses"][i]["category"] = new_category
                user_manager.save(user_data)

        total_expenses += user_data["expenses"][i]["value"] or 0

    # Кнопка добавления и итог
    add_col, total_col = st.columns([0.6, 0.4])
    with add_col:
        if st.button("+ Добавить расход", use_container_width=True, key=f"add_expense_{username}", 
                    type="secondary"):
            user_data["expenses"].append(
                {"name": "", "value": 0.0, "category": user_data["expense_categories"][0]}
            )
            user_manager.save(user_data)
            st.rerun()
    with total_col:
        st.metric("Итого", f"{format_currency(total_expenses)} ₽", label_visibility="collapsed")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Финансовый обзор
balance_after_expenses = total_income - total_expenses

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📊 Финансовый обзор</div>", unsafe_allow_html=True)
metric_cols = st.columns(3)
with metric_cols[0]:
    st.metric("Общий доход", f"{format_currency(total_income)} ₽")
with metric_cols[1]:
    st.metric("Общие расходы", f"{format_currency(total_expenses)} ₽")
with metric_cols[2]:
    st.metric("Свободные средства", f"{format_currency(balance_after_expenses)} ₽")

if balance_after_expenses < 0:
    st.error(f"⚠️ Дефицит бюджета: {format_currency(abs(balance_after_expenses))} ₽")
    st.warning("Рекомендуем увеличить доходы или уменьшить расходы")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Накопления
savings_cols = st.columns([2, 1])
with savings_cols[0]:
    savings_percentage = st.slider(
        "Процент накоплений от свободных средств",
        0,
        100,
        user_data["savings_percentage"],
        format="%d%%",
    )
    if savings_percentage != user_data["savings_percentage"]:
        user_data["savings_percentage"] = savings_percentage
        user_manager.save(user_data)

savings_amount = balance_after_expenses * (savings_percentage / 100)
disposable_income = balance_after_expenses - savings_amount
daily_budget = disposable_income / days_in_period if days_in_period > 0 else 0

with savings_cols[1]:
    st.markdown(
        f"""
        <div style="text-align:center; background: var(--surface-dark); border-radius: var(--radius-lg); border: 1px solid var(--border); padding: 1rem;">
            <div style="color: var(--text-secondary);">Накопления</div>
            <div style="font-size:1.4rem; font-weight:600; color: var(--primary-dark);">{format_currency(savings_amount)} ₽</div>
            <div style="color: var(--text-tertiary);">{savings_percentage}% от свободных средств</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="balance-card">
        <div class="label">БЮДЖЕТ НА ПЕРИОД</div>
        <div class="value">{format_currency(disposable_income)} ₽</div>
        <div class="subvalue">{days_in_period} дней • {format_currency(daily_budget)} ₽ в день</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# КАЛЕНДАРЬ И ЕЖЕДНЕВНЫЕ ТРАТЫ
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📅 Контроль ежедневных расходов</div>", unsafe_allow_html=True)

# Улучшенный выбор даты
selected_day = render_date_picker(start_date, end_date, st.session_state.selected_day, user_data, daily_budget)

# Обновляем выбранный день
st.session_state.selected_day = selected_day
selected_key = selected_day.isoformat()

# Форма добавления траты
st.markdown("### Добавить трату")

if selected_key not in user_data["daily_spends"]:
    user_data["daily_spends"][selected_key] = []

# Форма ввода
input_cols = st.columns([2, 1, 1])
with input_cols[0]:
    spend_desc = st.text_input("Название расхода", key=f"spend_desc_{selected_key}", 
                              placeholder="На что потратили?")
with input_cols[1]:
    spend_amount = st.number_input("Сумма", min_value=0.0, step=50.0, format="%.0f", 
                                   key=f"spend_amount_{selected_key}", value=0.0,
                                   placeholder="₽")
with input_cols[2]:
    st.markdown("<div style='height: 44px; display: flex; align-items: end; gap: 0.5rem;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        add_clicked = st.button("➕ Добавить", key=f"add_spend_{selected_key}", 
                               use_container_width=True, type="primary")
    with col2:
        remove_clicked = st.button("➖ Удалить", key=f"remove_spend_{selected_key}", 
                                  use_container_width=True, type="secondary")
    st.markdown("</div>", unsafe_allow_html=True)

if add_clicked:
    if spend_desc and spend_amount > 0:
        user_data["daily_spends"][selected_key].append(
            {"desc": spend_desc, "amount": spend_amount, "time": dt.now().strftime("%H:%M")}
        )
        user_manager.save(user_data)
        st.session_state.expense_page = 0
        st.rerun()
    else:
        st.warning("Введите название и сумму расхода")

# Список трат за день
st.markdown("### Траты за день")

spends_today = user_data["daily_spends"].get(selected_key, [])

if spends_today:
    # Пагинация
    items_per_page = 10
    total_pages = max(1, (len(spends_today) + items_per_page - 1) // items_per_page)
    current_page = st.session_state.expense_page
    start_idx = current_page * items_per_page
    end_idx = min((current_page + 1) * items_per_page, len(spends_today))
    
    # Отображение трат
    for idx in range(start_idx, end_idx):
        spend = spends_today[idx]
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{spend['desc']}**")
        
        with col2:
            st.markdown(f"**{format_currency(spend['amount'])} ₽**")
        
        with col3:
            if st.button("🗑", key=f"delete_{selected_key}_{idx}"):
                user_data["daily_spends"][selected_key].pop(idx)
                user_manager.save(user_data)
                st.rerun()
    
    # Пагинационные кнопки
    if total_pages > 1:
        pag_cols = st.columns([1, 2, 1])
        with pag_cols[0]:
            if current_page > 0:
                if st.button("◀️ Назад", key=f"prev_page_{selected_key}"):
                    st.session_state.expense_page = current_page - 1
                    st.rerun()
        with pag_cols[1]:
            st.markdown(f'<div style="text-align: center; padding: 0.5rem;">Страница {current_page + 1} из {total_pages}</div>', 
                       unsafe_allow_html=True)
        with pag_cols[2]:
            if current_page < total_pages - 1:
                if st.button("Вперёд ▶️", key=f"next_page_{selected_key}"):
                    st.session_state.expense_page = current_page + 1
                    st.rerun()
else:
    st.info("На этот день нет трат. Добавьте первую трату выше.")

# Статистика дня (ПОСЛЕ списка трат)
st.markdown("### Статистика дня")

# Вычисляем статистику для выбранного дня
rollover = 0.0
selected_budget = daily_budget
selected_spent = 0

for i in range(days_in_period):
    day = start_date + datetime.timedelta(days=i)
    day_key = day.isoformat()
    day_spent = sum(item["amount"] for item in user_data["daily_spends"].get(day_key, []))
    day_budget = daily_budget + rollover
    
    if day == selected_day:
        selected_budget = day_budget
        selected_spent = day_spent
        selected_balance = day_budget - day_spent
        break
    
    rollover = max(day_budget - day_spent, 0)

# Прогресс-бар
progress_percent = min((selected_spent / selected_budget * 100) if selected_budget > 0 else 0, 100)
progress_class = "over" if selected_spent > selected_budget else "under"

st.markdown(
    f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>Использовано: {progress_percent:.1f}%</span>
            <span>{format_currency(selected_spent)} / {format_currency(selected_budget)} ₽</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill {progress_class}" style="width: {progress_percent}%;"></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Три метрики
stats_cols = st.columns(3)

with stats_cols[0]:
    st.metric("Бюджет дня", f"{format_currency(selected_budget)} ₽")

with stats_cols[1]:
    st.metric("Потрачено", f"{format_currency(selected_spent)} ₽")

with stats_cols[2]:
    balance_color = "normal"
    if selected_balance >= 0:
        delta = f"+{format_currency(selected_balance)} ₽"
    else:
        delta = f"{format_currency(selected_balance)} ₽"
    
    st.metric("Остаток на завтра", f"{format_currency(selected_balance)} ₽", delta=delta)

st.markdown("</div>", unsafe_allow_html=True)

# ЭКСПОРТ ШАБЛОНА
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📤 Экспорт шаблона</div>", unsafe_allow_html=True)

# Создаем текстовый шаблон (без openpyxl)
export_data = create_simple_export(
    user_data=user_data,
    username=username,
    user_info=user_info,
    start_date=start_date,
    end_date=end_date,
    total_income=total_income,
    total_expenses=total_expenses,
    disposable_income=disposable_income,
    daily_budget=daily_budget,
    days_in_period=days_in_period
)

st.download_button(
    label="📥 Скачать шаблон за период (TXT)",
    data=export_data,
    file_name=f"финансовый_шаблон_{username}_{start_date.strftime('%Y-%m-%d')}.txt",
    mime="text/plain",
    use_container_width=True,
    type="primary",
    key="download_template"
)

st.markdown(
    """
    <div style="margin-top: 1rem; padding: 1rem; background: var(--surface-light); border-radius: var(--radius-md); border: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Что входит в шаблон:</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem;">
            <div>• 📊 Основные финансовые показатели</div>
            <div>• 💰 Свод постоянных доходов и расходов</div>
            <div>• 📅 Таблица для ручного ввода ежедневных трат</div>
            <div>• 💡 Подсказки по использованию</div>
            <div>• 🧮 Готовый формат для заполнения в Excel или Google Sheets</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# Футер
st.markdown(
    f"""
    <div style="text-align:center; color: var(--text-secondary); font-size: 0.9rem; padding: 1.5rem 0;">
        <div>Вы вошли как: {username} • Все данные сохраняются автоматически</div>
        <div>Финансовый Планнер • {datetime.date.today().year}</div>
    </div>
    """,
    unsafe_allow_html=True,
)