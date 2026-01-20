import datetime
import json
import locale
import os
from datetime import datetime as dt

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
    white-space: normal !important;
    word-break: break-word;
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
    font-size: 1.35rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
    line-height: 1.6;
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
    font-size: 2rem;
    font-weight: 700;
}

.balance-card .label,
.balance-card .subvalue {
    color: rgba(255, 255, 255, 0.85);
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div,
.stDateInput input {
    width: 100% !important;
}

.mini-calendar {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
}

.mini-calendar .week-row {
    display: flex;
    gap: 0.35rem;
    flex-wrap: nowrap;
}

.mini-calendar .day-button {
    flex: 1;
}

.mini-calendar .day-button button {
    width: 100%;
    padding: 0.35rem 0.25rem !important;
    font-size: 0.85rem !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface-light) !important;
    color: var(--text-primary) !important;
    min-height: 36px !important;
}

.mini-calendar .day-button.selected button {
    background: var(--primary-soft) !important;
    border-color: var(--primary) !important;
    color: var(--primary-dark) !important;
    font-weight: 600 !important;
}

.quick-input {
    display: flex;
    gap: 0.75rem;
    align-items: end;
    flex-wrap: wrap;
}

.quick-input .button-group {
    display: flex;
    gap: 0.5rem;
}

.expense-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.75rem;
}

.expense-tag {
    background: var(--surface-dark);
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    font-size: 0.85rem;
    display: flex;
    gap: 0.4rem;
    align-items: center;
    border: 1px solid var(--border);
}

.expense-tag button {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 0.85rem;
}

.dashboard-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
}

.dashboard-item {
    background: var(--surface-light);
    padding: 0.85rem 1rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
}

.dashboard-item .value {
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 0.35rem;
}

@media (max-width: 900px) {
    .main .block-container {
        padding: 1rem !important;
    }

    .section-card {
        padding: 1.1rem;
    }

    .quick-input {
        flex-direction: column;
        align-items: stretch;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column;
        gap: 0.75rem;
    }

    [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    .mini-calendar .day-button button {
        font-size: 0.75rem !important;
        padding: 0.3rem 0.2rem !important;
        min-height: 32px !important;
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


st.markdown("<h1>💰 Финансовый Планнер</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Контроль бюджета, ежедневные траты и понятная аналитика.</div>",
    unsafe_allow_html=True,
)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

registration_success = False

if st.session_state.get("authentication_status") is not True:
    auth_tabs = st.tabs(["🔐 Вход", "📝 Регистрация"])
    with auth_tabs[0]:
        name, authentication_status, username = authenticator.login("Вход", "main")
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
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

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


st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📅 Контроль ежедневных расходов</div>", unsafe_allow_html=True)

period_dates = [start_date + datetime.timedelta(days=i) for i in range(days_in_period)]

if "selected_day" not in st.session_state:
    today = datetime.date.today()
    st.session_state.selected_day = today if start_date <= today <= end_date else start_date


def select_day(day):
    st.session_state.selected_day = day


st.markdown("<div class='mini-calendar'>", unsafe_allow_html=True)
week = []
for day in period_dates:
    week.append(day)
    if len(week) == 7:
        cols = st.columns(7)
        for idx, col in enumerate(cols):
            current_day = week[idx]
            is_selected = current_day == st.session_state.selected_day
            label = f"{current_day.day}"
            if current_day == datetime.date.today():
                label = f"🔴 {label}"
            if is_selected:
                label = f"✅ {label}"
            with col:
                st.markdown(
                    f"<div class=\"day-button{' selected' if is_selected else ''}\">",
                    unsafe_allow_html=True,
                )
                st.button(label, key=f"day_{current_day.isoformat()}", on_click=select_day, args=(current_day,))
                st.markdown("</div>", unsafe_allow_html=True)
        week = []

if week:
    cols = st.columns(7)
    for idx in range(7):
        if idx < len(week):
            current_day = week[idx]
            is_selected = current_day == st.session_state.selected_day
            label = f"{current_day.day}"
            if current_day == datetime.date.today():
                label = f"🔴 {label}"
            if is_selected:
                label = f"✅ {label}"
            with cols[idx]:
                st.markdown(
                    f"<div class=\"day-button{' selected' if is_selected else ''}\">",
                    unsafe_allow_html=True,
                )
                st.button(label, key=f"day_{current_day.isoformat()}", on_click=select_day, args=(current_day,))
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            cols[idx].markdown(" ")

st.markdown("</div>", unsafe_allow_html=True)

selected_day = st.session_state.selected_day
selected_key = selected_day.isoformat()

st.markdown(
    f"<div style='margin-top: 1rem; font-weight: 600;'>Выбранный день: {selected_day.strftime('%d %B %Y')}</div>",
    unsafe_allow_html=True,
)

if selected_key not in user_data["daily_spends"]:
    user_data["daily_spends"][selected_key] = []

input_cols = st.columns([2.2, 1, 0.6])
with input_cols[0]:
    spend_desc = st.text_input("Название расхода", key=f"spend_desc_{selected_key}")
with input_cols[1]:
    spend_amount = st.number_input("Сумма", min_value=0.0, step=50.0, format="%.0f", key=f"spend_amount_{selected_key}")
with input_cols[2]:
    st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
    add_clicked = st.button("+", key=f"add_spend_{selected_key}")
    remove_clicked = st.button("-", key=f"remove_spend_{selected_key}")

if add_clicked:
    if spend_desc and spend_amount > 0:
        user_data["daily_spends"][selected_key].append(
            {"desc": spend_desc, "amount": spend_amount, "time": dt.now().strftime("%H:%M")}
        )
        user_manager.save(user_data)
        st.rerun()
    else:
        st.warning("Введите название и сумму расхода")

if remove_clicked:
    if user_data["daily_spends"][selected_key]:
        user_data["daily_spends"][selected_key].pop()
        user_manager.save(user_data)
        st.rerun()
    else:
        st.info("Нет расходов для удаления")

spends_today = user_data["daily_spends"].get(selected_key, [])

if spends_today:
    st.markdown("<div class='expense-tags'>", unsafe_allow_html=True)
    for idx, spend in enumerate(spends_today):
        tag_cols = st.columns([0.9, 0.1])
        with tag_cols[0]:
            st.markdown(
                f"<div class='expense-tag'>💸 {spend['desc']} • {format_currency(spend['amount'])} ₽</div>",
                unsafe_allow_html=True,
            )
        with tag_cols[1]:
            if st.button("×", key=f"remove_tag_{selected_key}_{idx}"):
                user_data["daily_spends"][selected_key].pop(idx)
                user_manager.save(user_data)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Добавьте расход — он появится здесь в виде тега")

rollover = 0.0
selected_budget = daily_budget
selected_spent = sum(item["amount"] for item in spends_today)
selected_balance = selected_budget - selected_spent
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
    rollover = day_balance

st.markdown("<div class='dashboard-row'>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="dashboard-item">
        <div>Бюджет дня</div>
        <div class="value">{format_currency(selected_budget)} ₽</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="dashboard-item">
        <div>Потрачено за день</div>
        <div class="value">{format_currency(selected_spent)} ₽</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="dashboard-item">
        <div>Останется на завтра</div>
        <div class="value" style="color: {'var(--secondary)' if selected_balance >= 0 else 'var(--danger)'};">
            {format_currency(selected_balance)} ₽
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📤 Экспорт отчета</div>", unsafe_allow_html=True)
user_info = config["credentials"]["usernames"].get(username, {})
report_text = f"""ФИНАНСОВЫЙ ОТЧЕТ
Пользователь: {user_info.get('name', username)}
Email: {user_info.get('email', '')}

Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
Дней в периоде: {days_in_period}

ДОХОДЫ:
Общий доход: {format_currency(total_income)} ₽

РАСХОДЫ:
Постоянные расходы: {format_currency(total_expenses)} ₽

НАКОПЕНИЯ:
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
)

if st.button("💾 Сохранить все данные", use_container_width=True, key=f"save_all_{username}"):
    user_manager.save(user_data)
    st.success("✅ Все данные сохранены")
    st.rerun()

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


