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

# --- ФУНКЦИИ СОХРАНЕНИЯ ДАННЫХ (ДОЛЖНЫ БЫТЬ ПЕРВЫМИ) ---
def save_user_data(username):
    """Сохранить все данные пользователя в JSON"""
    if username:
        user_data = {
            'incomes': st.session_state.incomes,
            'expenses': st.session_state.expenses,
            'daily_spends': st.session_state.daily_spends,
            'savings_percentage': st.session_state.savings_percentage,
            'categories': st.session_state.categories,
            'expense_categories': st.session_state.expense_categories
        }
        
        os.makedirs('user_data', exist_ok=True)
        filename = f'user_data/{username}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        return True
    return False

def init_user_session(username):
    """Инициализировать или загрузить данные пользователя"""
    user_data_file = f'user_data/{username}.json'
    
    if os.path.exists(user_data_file):
        # Загрузить сохраненные данные
        with open(user_data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        # Восстановить из сохраненных данных
        for key in ['incomes', 'expenses', 'daily_spends', 'savings_percentage']:
            if key in saved_data:
                st.session_state[key] = saved_data[key]
    else:
        # Инициализировать новые данные
        init_session_state()
    
    return True

def init_session_state():
    """Инициализация session_state"""
    defaults = {
        'incomes': [{"name": "Зарплата", "value": 50000.0, "category": "Основной"}],
        'expenses': [{"name": "Квартира", "value": 15000.0, "category": "Жилье"}],
        'daily_spends': {},
        'savings_percentage': 15,
        'categories': ["Основной", "Дополнительный", "Инвестиции", "Подарки", "Фриланс"],
        'expense_categories': ["Жилье", "Еда", "Транспорт", "Развлечения", "Здоровье", "Образование", "Покупки", "Прочее"],
        'show_all_days': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- НАСТРОЙКА АВТОРИЗАЦИИ ---
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

# --- АВТОРИЗАЦИЯ ---
name, authentication_status, username = authenticator.login('Вход в систему', 'main')

if authentication_status is False:
    st.error("❌ Неверный логин или пароль")
    st.stop()

if authentication_status is None:
    st.warning("🔐 Пожалуйста, введите логин и пароль")
    st.stop()

# --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ ПОЛЬЗОВАТЕЛЯ ---
init_user_session(username)

# --- ОСНОВНОЕ ПРИЛОЖЕНИЕ ---
st.set_page_config(
    layout="wide",
    page_title="💰 Финансовый Планнер",
    page_icon="💸",
    initial_sidebar_state="collapsed"
)

# --- НАСТРОЙКИ И СТИЛИ ---
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    pass

def format_currency(value):
    return f"{value:,.2f}".replace(',', ' ') if isinstance(value, (int, float)) else value

CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root {
    --primary: #4F46E5; --primary-light: #6366F1; --primary-dark: #3730A3; --secondary: #10B981; --danger: #EF4444; --warning: #F59E0B; --success: #10B981; --surface: #FFFFFF; --surface-light: #F9FAFB; --surface-dark: #F3F4F6; --border: #E5E7EB; --border-light: #F3F4F6; --text-primary: #111827; --text-secondary: #6B7280; --text-tertiary: #9CA3AF; --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05); --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08); --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08); --radius-sm: 6px; --radius-md: 10px; --radius-lg: 14px; --radius-xl: 20px;
}
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
body {
    background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%); color: var(--text-primary);
}
.stApp {
    background: transparent; max-width: 1400px !important; margin: 0 auto !important; padding: 0 20px !important;
}
.main .block-container {
    max-width: 1400px !important; padding-left: 2rem !important; padding-right: 2rem !important; padding-top: 1rem !important; padding-bottom: 1rem !important;
}
.main-title {
    text-align: center; color: var(--text-primary); font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem; letter-spacing: -0.025em;
}
.subtitle {
    color: var(--text-secondary); text-align: center; font-weight: 400; font-size: 1.1rem; margin-bottom: 2rem; line-height: 1.5;
}
.section-title {
    font-size: 1.4rem; font-weight: 600; color: var(--text-primary); margin-bottom: 1.2rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border-light);
}
.section-container {
    background: var(--surface); border-radius: var(--radius-xl); padding: 1.8rem; margin-bottom: 1.8rem; border: 1px solid var(--border); box-shadow: var(--shadow-sm); width: 100% !important;
}
.balance-card {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; border-radius: var(--radius-xl); padding: 2rem; text-align: center; margin: 1.5rem 0; position: relative; overflow: hidden;
}
.balance-label {
    font-size: 0.95rem; opacity: 0.9; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-transform: uppercase;
}
.balance-value {
    font-size: 2.8rem; font-weight: 700; margin: 0.5rem 0; letter-spacing: -0.025em;
}
.balance-subvalue {
    font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    border-radius: var(--radius-md) !important; border: 1px solid var(--border) !important; padding: 0.6rem 0.8rem !important; font-size: 0.95rem !important; width: 100% !important; min-width: 0 !important; max-width: none !important; overflow: visible !important; white-space: normal !important; text-overflow: clip !important;
}
.stSelectbox > div {
    min-width: 150px !important; max-width: none !important;
}
.stTextInput > div {
    min-width: 200px !important; max-width: none !important;
}
.stNumberInput > div {
    min-width: 120px !important; max-width: none !important;
}
[data-testid="stMetric"] {
    min-width: 180px !important; max-width: none !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important; font-weight: 700 !important; white-space: nowrap !important; overflow: visible !important; text-overflow: clip !important; max-width: none !important;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important; white-space: nowrap !important; overflow: visible !important; text-overflow: clip !important; max-width: none !important;
}
[data-testid="stColumn"] > div {
    min-width: 0 !important; max-width: none !important;
}
.input-row {
    display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; width: 100%;
}
.input-field {
    flex: 1; min-width: 0;
}
.spend-bubble {
    background: var(--surface-dark); border-radius: var(--radius-md); padding: 0.5rem 0.9rem; margin: 0.25rem; display: inline-flex; align-items: center; gap: 0.6rem; font-size: 0.85rem; border: 1px solid var(--border-light); white-space: nowrap; max-width: 100%; overflow: visible;
}
.compact-table-container {
    background: var(--surface); border-radius: var(--radius-lg); border: 1px solid var(--border-light); overflow: hidden; margin-top: 1rem;
}
.table-header {
    display: grid; grid-template-columns: 180px 150px 150px 150px 250px; gap: 1rem; padding: 1rem; background: var(--surface-dark); border-bottom: 1px solid var(--border); font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); width: 100%;
}
.table-row {
    display: grid; grid-template-columns: 180px 150px 150px 150px 250px; gap: 1rem; padding: 1rem; border-bottom: 1px solid var(--border-light); align-items: center; width: 100%;
}
.table-row:hover {
    background: var(--surface-light);
}
.table-cell {
    min-width: 0; overflow: visible; white-space: normal; word-wrap: break-word;
}
.divider {
    height: 1px; background: var(--border-light); margin: 1.5rem 0;
}
.stButton > button {
    border-radius: var(--radius-md) !important; font-weight: 500 !important; font-size: 0.9rem !important; padding: 0.6rem 1.2rem !important; min-width: auto !important; white-space: nowrap !important;
}
.stSlider > div {
    min-width: 300px !important; max-width: none !important;
}
div[data-testid="column"] {
    min-width: 0 !important; max-width: none !important;
}
.streamlit-expanderHeader {
    font-size: 1rem !important;
}
.date-cell {
    min-width: 180px !important;
}
.amount-cell {
    min-width: 120px !important; font-family: 'Inter', monospace !important; font-weight: 500 !important;
}
input::placeholder,
textarea::placeholder {
    color: var(--text-tertiary) !important; opacity: 0.7 !important;
}
"""
st.markdown(f"<style>{CSS_STYLE}</style>", unsafe_allow_html=True)

# --- SESSION STATE ---
def init_session_state():
    defaults = {
        'incomes': [{"name": "Зарплата", "value": 50000.0, "category": "Основной"}],
        'expenses': [{"name": "Квартира", "value": 15000.0, "category": "Жилье"}],
        'daily_spends': {},
        'savings_percentage': 15,
        'categories': ["Основной", "Дополнительный", "Инвестиции", "Подарки", "Фриланс"],
        'expense_categories': ["Жилье", "Еда", "Транспорт", "Развлечения", "Здоровье", "Образование", "Покупки", "Прочее"],
        'show_all_days': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- ФУНКЦИИ ---
def reset_days_view():
    st.session_state.show_all_days = False

def add_item(item_type, category=None):
    if item_type == 'incomes':
        st.session_state.incomes.append({
            "name": "", "value": 0.0, "category": category or st.session_state.categories[0]
        })
    else:
        st.session_state.expenses.append({
            "name": "", "value": 0.0, "category": category or st.session_state.expense_categories[0]
        })
    
    save_user_data(username)  # ← автосохранение
    st.rerun()  # обновить интерфейс

def remove_item(item_type, index):
    if item_type == 'incomes':
        st.session_state.incomes.pop(index)
    else:
        st.session_state.expenses.pop(index)
    save_user_data(username)  # ← автосохранение

def add_daily_spend(day_key, desc, amount, category="Еда"):
    if day_key not in st.session_state.daily_spends:
        st.session_state.daily_spends[day_key] = []
    if desc and amount > 0:
        st.session_state.daily_spends[day_key].append({
            "desc": desc, "amount": amount, "category": category, "time": dt.now().strftime("%H:%M")
        })
        save_user_data(username)  # ← автосохранение
        return True  # ← ДОЛЖЕН БЫТЬ ТАКОЙ ЖЕ ОТСТУП КАК У save_user_data ВЫШЕ!
    return False  # ← правильный отступ
    

def remove_daily_spend(day_key, index):
    if day_key in st.session_state.daily_spends and 0 <= index < len(st.session_state.daily_spends[day_key]):
        st.session_state.daily_spends[day_key].pop(index)
        save_user_data(username)  # ← автосохранение (ДОБАВИТЬ ОТСТУП!)
    # Нужен return True или хотя бы pass

def calculate_metrics():
    total_income = sum(item['value'] for item in st.session_state.incomes)
    total_expenses = sum(item['value'] for item in st.session_state.expenses)
    balance_after_expenses = total_income - total_expenses
    if balance_after_expenses >= 0:
        savings_percentage = st.session_state.get('savings_percentage', 15)
        savings_amount = balance_after_expenses * (savings_percentage / 100)
        disposable_income = balance_after_expenses - savings_amount
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance_after_expenses,
            'savings_percentage': savings_percentage,
            'savings_amount': savings_amount,
            'disposable_income': disposable_income
        }
    return None

# --- ШАПКА С ИНФОРМАЦИЕЙ О ПОЛЬЗОВАТЕЛЕ ---
user_col1, user_col2, user_col3 = st.columns([2, 1, 1])
with user_col1:
    st.markdown(f'<div class="main-title">💰 Финансовый Планнер</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Простое управление бюджетом • Аналитика в реальном времени • Минималистичный дизайн</div>', unsafe_allow_html=True)

with user_col3:
    # Получаем информацию о пользователе из config
    user_info = config['credentials']['usernames'].get(username, {})
    display_name = user_info.get('name', username)
    st.info(f"👤 {display_name}")
    authenticator.logout('Выйти', 'main')

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 1. ПЕРИОД РАСЧЕТА ---
with st.container():
    st.markdown('<div class="section-title">📅 Период расчета</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])
    with col1:
        start_date = st.date_input(
            "Начало периода",
            datetime.date.today(),
            format="DD.MM.YYYY",
            key="start_date_input",
            on_change=reset_days_view
        )
    with col2:
        end_date = st.date_input(
            "Конец периода",
            datetime.date.today() + datetime.timedelta(days=30),
            format="DD.MM.YYYY",
            key="end_date_input",
            on_change=reset_days_view
        )
    with col3:
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

# --- 2. ДОХОДЫ И РАСХОДЫ ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="section-title">💸 Доходы</div>', unsafe_allow_html=True)
    total_income = 0
    for i, income in enumerate(st.session_state.incomes):
        cols = st.columns([0.45, 0.25, 0.2, 0.1], gap="small")
        with cols[0]:
            st.session_state.incomes[i]['name'] = st.text_input("Название дохода", value=income['name'], key=f"in_name_{i}", label_visibility="collapsed", placeholder="Источник дохода")
        with cols[1]:
            st.session_state.incomes[i]['value'] = st.number_input("Сумма", value=float(income['value']), step=1000.0, format="%.0f", key=f"in_value_{i}", label_visibility="collapsed", placeholder="0 ₽")
        with cols[2]:
            st.session_state.incomes[i]['category'] = st.selectbox("Категория", st.session_state.categories, index=st.session_state.categories.index(income['category']) if income['category'] in st.session_state.categories else 0, key=f"in_cat_{i}", label_visibility="collapsed")
        with cols[3]:
            if len(st.session_state.incomes) > 1:
                if st.button("🗑", key=f"remove_income_{i}", help="Удалить доход", use_container_width=True, key="button_1"):
                    remove_item('incomes', i)
                    st.rerun()
        total_income += st.session_state.incomes[i]['value'] or 0
    add_col, total_col = st.columns([0.7, 0.3])
    with add_col:
        if st.button("+ Добавить доход", use_container_width=True, key="button_2", type="secondary"):
            add_item('incomes')
            st.rerun()
    with total_col:
        st.metric("Итого доходов", f"{format_currency(total_income)} ₽")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">🧾 Расходы</div>', unsafe_allow_html=True)
    total_expenses = 0
    for i, expense in enumerate(st.session_state.expenses):
        cols = st.columns([0.45, 0.25, 0.2, 0.1], gap="small")
        with cols[0]:
            st.session_state.expenses[i]['name'] = st.text_input("Название расхода", value=expense['name'], key=f"ex_name_{i}", label_visibility="collapsed", placeholder="Статья расхода")
        with cols[1]:
            st.session_state.expenses[i]['value'] = st.number_input("Сумма", value=float(expense['value']), step=1000.0, format="%.0f", key=f"ex_value_{i}", label_visibility="collapsed", placeholder="0 ₽")
        with cols[2]:
            st.session_state.expenses[i]['category'] = st.selectbox("Категория", st.session_state.expense_categories, index=st.session_state.expense_categories.index(expense['category']) if expense['category'] in st.session_state.expense_categories else 0, key=f"ex_cat_{i}", label_visibility="collapsed")
        with cols[3]:
            if len(st.session_state.expenses) > 1:
                if st.button("🗑", key=f"remove_expense_{i}", help="Удалить расход", use_container_width=True, key="button_3"):
                    remove_item('expenses', i)
                    st.rerun()
        total_expenses += st.session_state.expenses[i]['value'] or 0
    add_col, total_col = st.columns([0.7, 0.3])
    with add_col:
        if st.button("+ Добавить расход", use_container_width=True, key="button_4", type="secondary"):
            add_item('expenses')
            st.rerun()
    with total_col:
        st.metric("Итого расходов", f"{format_currency(total_expenses)} ₽")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 3. БЮДЖЕТ И НАКОПЛЕНИЯ ---
metrics = calculate_metrics()
if metrics:
    balance = metrics['balance']
    if balance >= 0:
        st.markdown('<div class="section-title">📊 Финансовый обзор</div>', unsafe_allow_html=True)
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("Общий доход", f"{format_currency(metrics['total_income'])} ₽")
        with metric_cols[1]:
            st.metric("Общие расходы", f"{format_currency(metrics['total_expenses'])} ₽")
        with metric_cols[2]:
            st.metric("Свободные средства", f"{format_currency(balance)} ₽")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🏦 Планирование накоплений</div>', unsafe_allow_html=True)
        col_slider, col_display = st.columns([2, 1])
        with col_slider:
            savings_percentage = st.slider(
                "Процент накоплений от свободных средств", 0, 100,
                st.session_state.get('savings_percentage', 15), format="%d%%", key="savings_slider",
                help="Какую часть свободных средств откладывать"
            )
            st.session_state.savings_percentage = savings_percentage
        
        savings_amount = balance * (savings_percentage / 100)
        disposable_income = balance - savings_amount
        daily_budget = disposable_income / days_in_period if days_in_period > 0 else 0
        
        with col_display:
            st.markdown(f'''
            <div style="text-align: center; padding: 1.2rem; background: var(--surface-dark); border-radius: var(--radius-lg); border: 1px solid var(--border); min-height: 120px;">
                <div style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Отложу на накопления</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: var(--primary); margin-bottom: 0.25rem;">{format_currency(savings_amount)} ₽</div>
                <div style="font-size: 0.9rem; color: var(--text-tertiary);">{savings_percentage}% от свободных средств</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown(f'''
        <div class="balance-card">
            <div class="balance-label">БЮДЖЕТ НА ПЕРИОД</div>
            <div class="balance-value">{format_currency(disposable_income)} ₽</div>
            <div class="balance-subvalue">Доступно на {days_in_period} дней • {format_currency(daily_budget)} ₽ в день</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.error(f"⚠️ Дефицит бюджета: {format_currency(abs(balance))} ₽")
        st.warning("Рекомендуем увеличить доходы или уменьшить расходы")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 4. КОНТРОЛЬ РАСХОДОВ ---
if metrics and metrics['balance'] >= 0:
    st.markdown('<div class="section-title">📱 Контроль ежедневных расходов</div>', unsafe_allow_html=True)
    with st.expander("💸 Быстрый ввод расхода на сегодня", expanded=False):
        cols = st.columns([0.4, 0.2, 0.25, 0.15])
        with cols[0]:
            quick_desc = st.text_input("Описание расхода", placeholder="Обед, кофе...", key="quick_desc")
        with cols[1]:
            quick_amount = st.number_input("Сумма", min_value=0.0, step=100.0, format="%.0f", key="quick_amount")
        with cols[2]:
            quick_category = st.selectbox("Категория", st.session_state.expense_categories, key="quick_cat")
        with cols[3]:
            st.write("") 
            if st.button("➕ Добавить", use_container_width=True, key="button_5", type="primary", key="quick_add"):
                today_key = datetime.date.today().strftime("%Y-%m-%d")
                if add_daily_spend(today_key, quick_desc, quick_amount, quick_category):
                    st.success("✅ Расход добавлен!")
                    st.rerun()
    
    with st.container():
        rollover = 0.0
        header_cols = st.columns([1.8, 1.5, 1.5, 1.5, 2.5])
        header_cols[0].markdown("**Дата**")
        header_cols[1].markdown("**Бюджет дня**")
        header_cols[2].markdown("**Потрачено**")
        header_cols[3].markdown("**Остаток**")
        header_cols[4].markdown("**Быстрый ввод**")

        st.markdown('<hr style="margin: 0.5rem 0; border-color: var(--border-light);">', unsafe_allow_html=True)
        
        if st.session_state.show_all_days:
            display_days = days_in_period
        else:
            display_days = min(days_in_period, 7)

        for i in range(display_days):
            current_day = start_date + datetime.timedelta(days=i)
            day_key = current_day.strftime("%Y-%m-%d")
            day_budget = daily_budget + rollover
            day_spends = st.session_state.daily_spends.get(day_key, [])
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
                    with st.form(key=f"form_{day_key}", clear_on_submit=True):
                        form_cols = st.columns([0.5, 0.3, 0.2])
                        desc = form_cols[0].text_input("", placeholder="Описание", key=f"desc_{day_key}", label_visibility="collapsed")
                        amount = form_cols[1].number_input("", min_value=0.0, step=100.0, format="%.0f", key=f"amount_{day_key}", label_visibility="collapsed", placeholder="0")
                        if form_cols[2].form_submit_button("➕", use_container_width=True):
                            if add_daily_spend(day_key, desc, amount, "Прочее"):
                                st.rerun()

                if day_spends:
                    st.markdown('<div style="margin-top: 0.5rem;">', unsafe_allow_html=True)
                    for j, spend in enumerate(day_spends):
                        b_cols = st.columns([0.9, 0.1])
                        with b_cols[0]:
                             st.markdown(f'<div class="spend-bubble" title="{spend["desc"]}: {format_currency(spend["amount"])} ₽ ({spend["category"]})"><span>{spend["desc"]}: <b>{format_currency(spend["amount"])} ₽</b></span></div>', unsafe_allow_html=True)
                        with b_cols[1]:
                            st.button("×", key=f"del_{day_key}_{j}", help="Удалить", on_click=remove_daily_spend, args=(day_key, j), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<hr style="margin: 0.5rem 0; border-color: var(--border-light);">', unsafe_allow_html=True)
        
        if not st.session_state.show_all_days and days_in_period > display_days:
            st.info(f"📅 Показано {display_days} из {days_in_period} дней.")
            if st.button(f"Показать все {days_in_period} дней", use_container_width=True, key="button_6", type="secondary"):
                st.session_state.show_all_days = True
                st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- 5. ЭКСПОРТ ---
st.markdown('<div class="section-title">📤 Экспорт отчета</div>', unsafe_allow_html=True)
if metrics and metrics['balance'] >= 0:
    col_stats, col_export = st.columns([1, 1])
    with col_stats:
        if st.session_state.daily_spends:
            total_spent = sum(sum(item['amount'] for item in spends) for spends in st.session_state.daily_spends.values())
            days_with_spends = len(st.session_state.daily_spends)
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
Процент накоплений: {st.session_state.get('savings_percentage', 15)}%
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
            type="primary"
        )
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- ФУТЕР ---
st.markdown(f"""
<div style="text-align: center; color: var(--text-secondary); font-size: 0.9rem; padding: 2rem 0;">
    <div style="margin-bottom: 0.5rem;">
        <span style="margin: 0 0.5rem;">👤 Вы вошли как: {username}</span>
        <span style="margin: 0 0.5rem;">•</span>
        <span style="margin: 0 0.5rem;">💡 Все данные сохраняются автоматически</span>
        <span style="margin: 0 0.5rem;">•</span>
        <span style="margin: 0 0.5rem;">📱 Адаптировано для всех устройств</span>
    </div>
    <div>Финансовый Планнер • Версия 5.0 • 2024 • Режим: {username}</div>
</div>
""", unsafe_allow_html=True)
# --- КНОПКА СОХРАНЕНИЯ ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
if st.button("💾 Сохранить все данные", use_container_width=True, key="button_7", key="save_all_data_button"):
    if save_user_data(username):
        st.success("✅ Данные сохранены!")
        st.rerun()  # обновить интерфейс
    else:
        st.error("❌ Ошибка сохранения")