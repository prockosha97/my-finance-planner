import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(layout="wide", page_title="🕵️‍♂️ Диагностика Авторизации")

st.title("Страница Диагностики")
st.warning("Это временная версия для отладки. Пожалуйста, сделайте скриншот или скопируйте и отправьте мне всё, что вы увидите на этой странице после попытки входа.")

# --- Шаг 1: Проверяем, читается ли config.yaml ---
st.header("Шаг 1: Содержимое `config.yaml`")
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    st.success("✅ Файл `config.yaml` успешно найден и прочитан.")
    st.write("Вот что я вижу внутри `config.yaml` (как его видит сервер):")
    st.json(config) 
except Exception as e:
    st.error(f"❌ ОШИБКА: Не удалось прочитать или обработать `config.yaml`.")
    st.exception(e)
    st.stop() 

# --- Шаг 2: Запускаем аутентификацию ---
st.header("Шаг 2: Попытка входа")
st.info("Сейчас появится форма входа. Пожалуйста, попробуйте войти, используя:\n\n*   Логин: `user1`\n*   Пароль: `pass1`")

try:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookies']['cookie_name'],
        config['cookies']['key'],
        config['cookies']['expiry_days']
    )
    authenticator.login()
except Exception as e:
    st.error(f"❌ ОШИБКА: Проблема при инициализации или вызове `authenticator.login()`.")
    st.exception(e)


# --- Шаг 3: Проверяем результат (session_state) ---
st.header("Шаг 3: Результат после вашей попытки входа")
st.write("Вот ключевые значения, которые хранятся в `st.session_state`:")

auth_status = st.session_state.get("authentication_status")
user_name = st.session_state.get("name")
username_login = st.session_state.get("username")

st.write(f"- `authentication_status`: **{auth_status}**")
st.write(f"- `name`: **{user_name}**")
st.write(f"- `username`: **{username_login}**")

# --- Шаг 4: Вывод ---
st.header("Шаг 4: Мой вывод на основе данных")
if auth_status:
    st.success("✅ СУДЯ ПО ДАННЫМ, ВХОД УСПЕШЕН!")
elif auth_status is False:
    st.error("❌ СУДЯ ПО ДАННЫМ, ВХОД НЕУДАЧЕН. Библиотека вернула `False`.")
    st.write("Это значит, что введенный пароль не совпал с хэшем из файла `config.yaml`.")
elif auth_status is None:
    st.warning("🟡 СУДЯ ПО ДАННЫМ, ПОПЫТКИ ВХОДА ЕЩЕ НЕ БЫЛО.")

st.info("Пожалуйста, сделайте скриншот этой страницы или скопируйте весь текст и отправьте мне.")
