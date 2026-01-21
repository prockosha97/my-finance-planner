import datetime
import json
import locale
import os
import pandas as pd
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
    word-break: keep-all;
    overflow-wrap: normal;
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
    white-space: nowrap;
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

/* Исправление полей ввода для всех устройств */
.stTextInput input,
.stNumberInput input,
.stSelectbox div,
.stDateInput input {
    width: 100% !important;
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    font-size: 14px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stSelectbox div:focus,
.stDateInput input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--primary-soft) !important;
}

/* Исправление выпадающих списков */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
}

.stSelectbox div[data-baseweb="select"] [role="listbox"] {
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
}

.stSelectbox div[data-baseweb="select"] [role="option"] {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    color: var(--text-primary) !important;
    background-color: var(--surface) !important;
}

.stSelectbox div[data-baseweb="select"] [role="option"]:hover {
    background-color: var(--surface-dark) !important;
}

div[data-testid="stTextInput"] small,
div[data-testid="stNumberInput"] small,
div[data-testid="stDateInput"] small,
div[data-testid="stSelectbox"] small {
    display: none !important;
}

/* Компактный календарь */
.compact-calendar {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-bottom: 1rem;
}

.calendar-day {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}

.calendar-day:hover {
    background-color: var(--surface-dark) !important;
}

.calendar-day.today {
    background-color: var(--primary-soft);
    color: var(--primary-dark);
    border-color: var(--primary);
}

.calendar-day.selected {
    background-color: var(--primary);
    color: white;
    font-weight: 600;
}

.calendar-day.over-budget {
    background-color: var(--danger-light);
    color: var(--danger);
}

.calendar-day.within-budget {
    background-color: var(--success-light);
    color: var(--secondary);
}

.calendar-day.inactive {
    color: var(--text-tertiary);
    cursor: default;
    background-color: var(--surface-light);
}

.calendar-day.empty {
    visibility: hidden;
}

.calendar-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-bottom: 8px;
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 600;
}

.calendar-month {
    text-align: center;
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: var(--text-primary);
    font-size: 1.1rem;
}

/* Список трат */
.expense-list {
    max-height: 400px;
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

.expense-item button {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 1.2rem;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
}

.expense-item .delete-btn {
    color: var(--danger);
}

.expense-item .delete-btn:hover {
    background-color: var(--danger-light);
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 1rem;
}

.pagination button {
    min-height: 44px !important;
    padding: 0.5rem 1rem !important;
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
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
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
.expense-form {
    display: flex;
    gap: 0.75rem;
    align-items: end;
    flex-wrap: wrap;
}

.expense-form .add-btn {
    background-color: var(--secondary) !important;
    color: white !important;
    border: none !important;
    min-height: 44px !important;
}

.expense-form .remove-btn {
    background-color: var(--danger) !important;
    color: white !important;
    border: none !important;
    min-height: 44px !important;
}

/* Кнопка экспорта */
.export-btn {
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
        padding: 1.1rem;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column;
        gap: 0.75rem;
    }

    [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Мобильные поля ввода */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div,
    .stDateInput input {
        font-size: 16px !important;
        min-height: 44px !important;
        padding: 0.75rem 1rem !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        padding: 0.75rem 1rem !important;
        font-size: 16px !important;
    }

    .compact-calendar {
        gap: 3px;
    }

    .calendar-day {
        font-size: 0.75rem;
    }

    .calendar-header {
        font-size: 0.7rem;
    }

    .expense-form {
        flex-direction: column;
        align-items: stretch;
    }

    .expense-form .stTextInput,
    .expense-form .stNumberInput {
        width: 100% !important;
    }

    .day-stats {
        grid-template-columns: 1fr;
        gap: 0.5rem;
    }

    .expense-item {
        padding: 0.5rem 0.75rem;
    }
}

@media (max-width: 600px) {
    .compact-calendar {
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
    }

    .calendar-day {
        font-size: 0.7rem;
        padding: 0.25rem;
    }

    .expense-item-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
    }
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


# Настройка сессии для запоминания входа
if 'login_username' not in st.session_state:
    st.session_state.login_username = None
if 'login_remember' not in st.session_state:
    st.session_state.login_remember = False

try:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)
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
    st.markdown("<div class='section-title'>📝 Регистрация</div>", unsafe_allow_html=True)
    with st.form(key="registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Логин*", placeholder="Придумайте логин")
            new_email = st.text_input("Email*", placeholder="your@email.com")
        with col2:
            new_name = st.text_input("Имя и фамилия*", placeholder="Иван Иванов")
            new_password = st.text_input("Пароль*", type="password")
            confirm_password = st.text_input("Подтвердите пароль*", type="password")

        submitted = st.form_submit_button("Зарегистрироваться", use_container_width=True, type="primary")
        if not submitted:
            return False

        if not all([new_username, new_email, new_name, new_password, confirm_password]):
            st.error("❌ Заполните все обязательные поля")
            return False

        if new_password != confirm_password:
            st.error("❌ Пароли не совпадают")
            return False

        if len(new_password) < 6:
            st.error("❌ Пароль должен быть не менее 6 символов")
            return False

        user_manager = UserDataManager(new_username)
        success, result = user_manager.register_new_user(new_username, new_email, new_name, new_password)

        if success:
            user_manager.save_new_user_to_config(result)
            user_data = user_manager.load()
            user_manager.save(user_data)
            st.success(f"✅ Пользователь {new_username} успешно зарегистрирован")
            st.info("Теперь вы можете войти в систему")
            return True

        st.error(f"❌ {result}")
        return False


def create_excel_template(user_data, username, user_info, start_date, end_date, 
                          total_income, total_expenses, disposable_income, daily_budget, days_in_period):
    """Создаёт Excel файл с шаблоном для заполнения"""
    
    # Создаём Excel writer
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Лист 1: Дашборд
        dashboard_data = {
            'Параметр': [
                'Пользователь',
                'Email',
                'Период',
                'Дней в периоде',
                'Общий доход',
                'Постоянные расходы',
                'Свободные средства',
                'Бюджет на период',
                'Бюджет на день',
                'Дата создания'
            ],
            'Значение': [
                user_info.get('name', username),
                user_info.get('email', ''),
                f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
                days_in_period,
                f"{format_currency(total_income)} ₽",
                f"{format_currency(total_expenses)} ₽",
                f"{format_currency(total_income - total_expenses)} ₽",
                f"{format_currency(disposable_income)} ₽",
                f"{format_currency(daily_budget)} ₽",
                datetime.date.today().strftime('%d.%m.%Y')
            ]
        }
        df_dashboard = pd.DataFrame(dashboard_data)
        df_dashboard.to_excel(writer, sheet_name='Дашборд', index=False)
        
        # Настройка ширины колонок для дашборда
        worksheet = writer.sheets['Дашборд']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 30
        
        # Лист 2: Постоянные доходы/расходы
        incomes_df = pd.DataFrame(user_data['incomes'])
        expenses_df = pd.DataFrame(user_data['expenses'])
        
        incomes_df.to_excel(writer, sheet_name='Постоянные', startrow=0, index=False)
        expenses_df.to_excel(writer, sheet_name='Постоянные', startrow=len(incomes_df) + 3, index=False)
        
        worksheet = writer.sheets['Постоянные']
        worksheet.cell(row=1, column=1, value='ДОХОДЫ:')
        worksheet.cell(row=len(incomes_df) + 3, column=1, value='РАСХОДЫ:')
        
        # Лист 3: Ежедневные траты
        days_data = []
        for i in range(days_in_period):
            current_date = start_date + datetime.timedelta(days=i)
            days_data.append({
                'Дата': current_date.strftime('%d.%m.%Y'),
                'Бюджет дня': daily_budget,
                'Трата 1': '',
                'Трата 2': '',
                'Трата 3': '',
                'Трата 4': '',
                'Трата 5': '',
                'Итого трат': '',
                'Остаток': ''
            })
        
        df_days = pd.DataFrame(days_data)
        df_days.to_excel(writer, sheet_name='Ежедневные траты', index=False)
        
        # Добавляем формулы для Excel
        worksheet = writer.sheets['Ежедневные траты']
        
        # Формулы для подсчёта итогов и остатков
        for i in range(2, len(days_data) + 2):
            # Формула для суммы трат (столбцы C-G)
            sum_formula = f'=SUM(C{i}:G{i})'
            worksheet.cell(row=i, column=8, value=sum_formula)
            
            # Формула для остатка (бюджет - траты)
            balance_formula = f'=B{i}-H{i}'
            worksheet.cell(row=i, column=9, value=balance_formula)
        
        # Настройка ширины колонок
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            worksheet.column_dimensions[column].width = adjusted_width
        
        # Лист 4: Подсказки
        tips_data = {
            'Совет': [
                '1. Заполняйте траты ежедневно',
                '2. Первые 5 строк - для самых крупных трат дня',
                '3. Остаток переносится на следующий день',
                '4. Красный цвет - перерасход бюджета',
                '5. Зелёный цвет - экономия'
            ],
            'Как использовать': [
                'Не откладывайте на потом',
                'Мелкие траты группируйте',
                'Автоматически рассчитывается в приложении',
                'Старайтесь не допускать',
                'Можно отложить на будущее'
            ]
        }
        df_tips = pd.DataFrame(tips_data)
        df_tips.to_excel(writer, sheet_name='Подсказки', index=False)
    
    return output.getvalue()


def render_compact_calendar(start_date, end_date, selected_day, daily_budgets, user_data):
    """Рендерит компактный календарь"""
    
    # Определяем первый день месяца и последний
    first_day = start_date.replace(day=1)
    last_day = end_date
    
    # Создаём сетку календаря
    st.markdown('<div class="calendar-month">' + 
                selected_day.strftime('%B %Y').title() + '</div>', unsafe_allow_html=True)
    
    # Заголовки дней недели
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    st.markdown('<div class="calendar-header">' + 
                ''.join([f'<div>{day}</div>' for day in weekdays]) + 
                '</div>', unsafe_allow_html=True)
    
    # Дни календаря
    days_grid = []
    
    # Пустые дни до первого числа
    first_weekday = first_day.weekday()  # 0 = понедельник
    for _ in range(first_weekday):
        days_grid.append({'day': '', 'date': None, 'class': 'empty'})
    
    # Все дни месяца
    current = first_day
    while current <= last_day:
        day_key = current.isoformat()
        day_spent = sum(item["amount"] for item in user_data["daily_spends"].get(day_key, []))
        
        # Определяем класс для дня
        day_class = "calendar-day"
        if current == datetime.date.today():
            day_class += " today"
        elif current == selected_day:
            day_class += " selected"
        
        # Проверяем бюджет для дня (упрощённо)
        daily_budget = daily_budgets.get(day_key, 0)
        if day_spent > daily_budget and day_spent > 0:
            day_class += " over-budget"
        elif day_spent <= daily_budget and day_spent > 0:
            day_class += " within-budget"
        
        days_grid.append({
            'day': current.day,
            'date': current,
            'class': day_class
        })
        
        current += datetime.timedelta(days=1)
    
    # Заполняем оставшиеся ячейки
    while len(days_grid) % 7 != 0:
        days_grid.append({'day': '', 'date': None, 'class': 'empty'})
    
    # Рендерим календарь
    html_days = []
    for i, day_info in enumerate(days_grid):
        if day_info['date']:
            html_days.append(f'<div class="{day_info["class"]}" onclick="selectDay(\'{day_info["date"].isoformat()}\')">{day_info["day"]}</div>')
        else:
            html_days.append(f'<div class="{day_info["class"]}"></div>')
    
    st.markdown(f'<div class="compact-calendar">{"".join(html_days)}</div>', unsafe_allow_html=True)
    
    # JavaScript для выбора дня
    st.markdown("""
    <script>
    function selectDay(dateStr) {
        const url = new URL(window.location);
        url.searchParams.set('selected_day', dateStr);
        window.history.pushState({}, '', url);
        window.location.reload();
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Обработка выбора дня из URL
    query_params = st.query_params
    if 'selected_day' in query_params:
        try:
            selected_date = datetime.date.fromisoformat(query_params['selected_day'])
            if start_date <= selected_date <= end_date:
                return selected_date
        except:
            pass
    
    return selected_day


st.markdown("<h1>💰 Финансовый Планнер</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Контроль бюджета, ежедневные траты и понятная аналитика.</div>",
    unsafe_allow_html=True,
)

registration_success = False

# Проверяем запомненного пользователя
if st.session_state.login_remember and st.session_state.login_username:
    try:
        # Пытаемся автоматически войти
        authenticator.login('auto_login', 'main')
        if st.session_state.get("authentication_status"):
            username = st.session_state.login_username
            st.session_state["username"] = username
            st.session_state["authentication_status"] = True
            st.session_state["name"] = config["credentials"]["usernames"][username]["name"]
    except:
        pass

if st.session_state.get("authentication_status") is not True:
    auth_tabs = st.tabs(["🔐 Вход", "📝 Регистрация"])
    with auth_tabs[0]:
        name, authentication_status, username = authenticator.login("Вход", "main")
        if authentication_status:
            st.session_state.login_username = username
            st.session_state.login_remember = True
        if authentication_status is False:
            st.error("❌ Неверный логин или пароль")
        if authentication_status is None:
            st.info("Введите логин и пароль")

    with auth_tabs[1]:
        registration_success = show_registration_form()

    if authentication_status is False:
        st.stop()

    if authentication_status is None and not registration_success:
        st.warning("🔐 Пожалуйста, войдите или зарегистрируйтесь")
        st.stop()

    if registration_success:
        st.rerun()

username = st.session_state.get("username")
if not username:
    st.warning("🔐 Пожалуйста, войдите в систему снова")
    st.stop()

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
    authenticator.logout("Выйти", "main")

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

income_expense_cols = st.columns(2)

with income_expense_cols[0]:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💸 Доходы</div>", unsafe_allow_html=True)
    total_income = 0.0
    for i, income in enumerate(user_data["incomes"]):
        with st.container():
            row = st.columns([2.2, 1, 1, 0.4])
            with row[0]:
                new_name = st.text_input(
                    "Название дохода",
                    value=income["name"],
                    key=f"income_name_{username}_{i}",
                )
            with row[1]:
                new_value = st.number_input(
                    "Сумма",
                    value=float(income["value"]),
                    step=1000.0,
                    format="%.0f",
                    key=f"income_value_{username}_{i}",
                )
            with row[2]:
                new_category = st.selectbox(
                    "Категория",
                    user_data["categories"],
                    index=user_data["categories"].index(income["category"])
                    if income["category"] in user_data["categories"]
                    else 0,
                    key=f"income_cat_{username}_{i}",
                )
            with row[3]:
                if len(user_data["incomes"]) > 1:
                    if st.button("🗑", key=f"income_remove_{username}_{i}"):
                        user_data["incomes"].pop(i)
                        user_manager.save(user_data)
                        st.rerun()

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

    add_col, total_col = st.columns([0.7, 0.3])
    with add_col:
        if st.button("+ Добавить доход", use_container_width=True, key=f"add_income_{username}"):
            user_data["incomes"].append({"name": "", "value": 0.0, "category": user_data["categories"][0]})
            user_manager.save(user_data)
            st.rerun()
    with total_col:
        st.metric("Итого", f"{format_currency(total_income)} ₽")
    st.markdown("</div>", unsafe_allow_html=True)

with income_expense_cols[1]:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🧾 Расходы</div>", unsafe_allow_html=True)
    total_expenses = 0.0
    for i, expense in enumerate(user_data["expenses"]):
        with st.container():
            row = st.columns([2.2, 1, 1, 0.4])
            with row[0]:
                new_name = st.text_input(
                    "Название расхода",
                    value=expense["name"],
                    key=f"expense_name_{username}_{i}",
                )
            with row[1]:
                new_value = st.number_input(
                    "Сумма",
                    value=float(expense["value"]),
                    step=500.0,
                    format="%.0f",
                    key=f"expense_value_{username}_{i}",
                )
            with row[2]:
                new_category = st.selectbox(
                    "Категория",
                    user_data["expense_categories"],
                    index=user_data["expense_categories"].index(expense["category"])
                    if expense["category"] in user_data["expense_categories"]
                    else 0,
                    key=f"expense_cat_{username}_{i}",
                )
            with row[3]:
                if len(user_data["expenses"]) > 1:
                    if st.button("🗑", key=f"expense_remove_{username}_{i}"):
                        user_data["expenses"].pop(i)
                        user_manager.save(user_data)
                        st.rerun()

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

    add_col, total_col = st.columns([0.7, 0.3])
    with add_col:
        if st.button("+ Добавить расход", use_container_width=True, key=f"add_expense_{username}"):
            user_data["expenses"].append(
                {"name": "", "value": 0.0, "category": user_data["expense_categories"][0]}
            )
            user_manager.save(user_data)
            st.rerun()
    with total_col:
        st.metric("Итого", f"{format_currency(total_expenses)} ₽")
    st.markdown("</div>", unsafe_allow_html=True)

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


# НОВЫЙ БЛОК: КАЛЕНДАРЬ И ЕЖЕДНЕВНЫЕ ТРАТЫ
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📅 Контроль ежедневных расходов</div>", unsafe_allow_html=True)

period_dates = [start_date + datetime.timedelta(days=i) for i in range(days_in_period)]

# Вычисляем бюджет для каждого дня с учётом переноса
daily_budgets = {}
rollover = 0.0
for day in period_dates:
    day_key = day.isoformat()
    day_spent = sum(item["amount"] for item in user_data["daily_spends"].get(day_key, []))
    day_budget = daily_budget + rollover
    daily_budgets[day_key] = day_budget
    day_balance = day_budget - day_spent
    rollover = max(day_balance, 0)  # Переносим только положительный остаток

# Определяем выбранный день
selected_day = st.session_state.get("selected_day", start_date)
if selected_day not in period_dates:
    selected_day = start_date

# Компактный календарь
st.markdown("### Календарь периода")
selected_day = render_compact_calendar(start_date, end_date, selected_day, daily_budgets, user_data)

# Сохраняем выбранный день в сессии
st.session_state.selected_day = selected_day

selected_key = selected_day.isoformat()

# Статистика дня
rollover = 0.0
selected_budget = daily_budget
selected_spent = 0
for day in period_dates:
    day_key = day.isoformat()
    day_spent = sum(item["amount"] for item in user_data["daily_spends"].get(day_key, []))
    day_budget = daily_budget + rollover
    day_balance = day_budget - day_spent
    
    if day == selected_day:
        selected_budget = day_budget
        selected_spent = day_spent
        selected_balance = day_balance
        break
    
    rollover = max(day_balance, 0)

# Отображение статистики дня
st.markdown(f"### {selected_day.strftime('%d %B %Y')}")

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

# Статистика дня
st.markdown('<div class="day-stats">', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="stat-item">
        <div class="stat-label">Бюджет дня</div>
        <div class="stat-value">{format_currency(selected_budget)} ₽</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="stat-item">
        <div class="stat-label">Потрачено</div>
        <div class="stat-value">{format_currency(selected_spent)} ₽</div>
    </div>
    """,
    unsafe_allow_html=True,
)

balance_class = "positive" if selected_balance >= 0 else "negative"
st.markdown(
    f"""
    <div class="stat-item">
        <div class="stat-label">Остаток на завтра</div>
        <div class="stat-value {balance_class}">{format_currency(selected_balance)} ₽</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)

# Список трат за день
st.markdown("### Траты за день")

if selected_key not in user_data["daily_spends"]:
    user_data["daily_spends"][selected_key] = []

spends_today = user_data["daily_spends"].get(selected_key, [])

# Пагинация
items_per_page = 10
if 'expense_page' not in st.session_state:
    st.session_state.expense_page = 0

total_pages = max(1, (len(spends_today) + items_per_page - 1) // items_per_page)
current_page = st.session_state.expense_page
start_idx = current_page * items_per_page
end_idx = min((current_page + 1) * items_per_page, len(spends_today))

# Отображение трат с пагинацией
if spends_today:
    st.markdown('<div class="expense-list">', unsafe_allow_html=True)
    
    for idx in range(start_idx, end_idx):
        spend = spends_today[idx]
        st.markdown(
            f"""
            <div class="expense-item">
                <div class="expense-item-info">
                    <span>💸 {spend['desc']}</span>
                    <span class="expense-item-amount">{format_currency(spend['amount'])} ₽</span>
                    <span class="expense-item-time">{spend.get('time', '')}</span>
                </div>
                <div class="expense-item-actions">
                    <button class="delete-btn" onclick="deleteExpense({idx})">-</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Пагинация
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if current_page > 0:
                if st.button("◀️ Назад", key=f"prev_page_{selected_key}"):
                    st.session_state.expense_page = current_page - 1
                    st.rerun()
        with col2:
            st.markdown(f'<div style="text-align: center; padding: 0.5rem;">Страница {current_page + 1} из {total_pages}</div>', unsafe_allow_html=True)
        with col3:
            if current_page < total_pages - 1:
                if st.button("Вперёд ▶️", key=f"next_page_{selected_key}"):
                    st.session_state.expense_page = current_page + 1
                    st.rerun()
else:
    st.info("На этот день нет трат. Добавьте первую трату ниже.")

# Форма добавления траты
st.markdown("### Добавить трату")

input_cols = st.columns([2, 1, 1])
with input_cols[0]:
    spend_desc = st.text_input("Название расхода", key=f"spend_desc_{selected_key}")
with input_cols[1]:
    spend_amount = st.number_input("Сумма", min_value=0.0, step=50.0, format="%.0f", 
                                   key=f"spend_amount_{selected_key}", value=0.0)
with input_cols[2]:
    st.markdown("<div style='height: 44px; display: flex; align-items: end;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        add_clicked = st.button("➕", key=f"add_spend_{selected_key}", use_container_width=True)
    with col2:
        remove_clicked = st.button("➖", key=f"remove_spend_{selected_key}", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if add_clicked:
    if spend_desc and spend_amount > 0:
        user_data["daily_spends"][selected_key].append(
            {"desc": spend_desc, "amount": spend_amount, "time": dt.now().strftime("%H:%M")}
        )
        user_manager.save(user_data)
        st.session_state.expense_page = 0  # Сбрасываем на первую страницу
        st.rerun()
    else:
        st.warning("Введите название и сумму расхода")

if remove_clicked:
    if user_data["daily_spends"][selected_key]:
        user_data["daily_spends"][selected_key].pop()
        user_manager.save(user_data)
        st.session_state.expense_page = 0  # Сбрасываем на первую страницу
        st.rerun()
    else:
        st.info("Нет расходов для удаления")

# JavaScript для удаления трат
st.markdown("""
<script>
function deleteExpense(index) {
    if (confirm("Удалить эту трату?")) {
        const url = new URL(window.location);
        url.searchParams.set('delete_expense', index);
        url.searchParams.set('selected_day', '%s');
        window.location.href = url.toString();
    }
}
</script>
""" % selected_key, unsafe_allow_html=True)

# Обработка удаления через URL
query_params = st.query_params
if 'delete_expense' in query_params and 'selected_day' in query_params:
    try:
        delete_idx = int(query_params['delete_expense'])
        delete_day = query_params['selected_day']
        if delete_day in user_data["daily_spends"] and 0 <= delete_idx < len(user_data["daily_spends"][delete_day]):
            user_data["daily_spends"][delete_day].pop(delete_idx)
            user_manager.save(user_data)
            # Очищаем параметры
            st.query_params.clear()
            st.rerun()
    except:
        pass

st.markdown("</div>", unsafe_allow_html=True)

# БЛОК ЭКСПОРТА
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📤 Экспорт шаблона</div>", unsafe_allow_html=True)

# Создание Excel файла
excel_data = create_excel_template(
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

# Кнопка скачивания
st.download_button(
    label="📥 Скачать шаблон за период (Excel)",
    data=excel_data,
    file_name=f"финансовый_шаблон_{username}_{start_date.strftime('%Y-%m-%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    type="primary",
    key="download_excel"
)

st.markdown(
    """
    <div style="margin-top: 1rem; padding: 1rem; background: var(--surface-light); border-radius: var(--radius-md); border: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Что входит в шаблон:</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem;">
            <div>• 📊 Дашборд с основными показателями</div>
            <div>• 💰 Свод постоянных доходов и расходов</div>
            <div>• 📅 Таблица для ручного ввода ежедневных трат</div>
            <div>• 🧮 Автоматические формулы для расчёта остатков</div>
            <div>• 💡 Подсказки по использованию</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div style="text-align:center; color: var(--text-secondary); font-size: 0.9rem; padding: 1.5rem 0;">
        <div>Вы вошли как: {username} • Все данные сохраняются автоматически</div>
        <div>Финансовый Планнер • 2024</div>
    </div>
    """,
    unsafe_allow_html=True,
)