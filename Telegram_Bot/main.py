#       https://t.me/YourBotUsername?start=unique_code
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
import logging
import asyncio
import sqlite3
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
# Экземпляр
BOT_TOKEN = "7307411243:AAFkaFIMOuh70njhnwUPki_OkBbdl5-SqWc"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Админ
admin_username = "Artemiy_Chernakov"
# Имя бота
bot_username = "Mentoring_for_juns_bot"

start_message2 = "Этот бот создан для комфортного взаимодействия джунов и менторов внутри команды. Мы уверены, что Менторинг бот станет незаменимым инструментом для развития вашей команды и повышения эффективности менторинга!"
message_for_jun = "🧭 Найдите свой путь. Менторинг бот поможет вам ориентироваться в образовательном треке, отслеживать свой прогресс, не пропустить важные этапы и получать обратную связь"
message_for_mentr = "🚀 Создайте пространство для успеха. Менторинг бот поможет вам организовать и оптимизировать процесс обучения джунов. Добавляйте участников, назначайте задачи, отслеживайте прогресс и получайте обратную связь"
welcome_mentor_message = "Добро пожаловать, Ментор! Теперь вам предстоит создать пространство команды и загрузить базу знаний"
ground_of_jun = "Добро пожаловать! Введи код пространства, которое создал для тебя твой ментор"
messafe_about_of_bot  = "Этот бот создан для комфортного взаимодействия джунов и менторов внутри команды. \n  Мы уверены, что Менторинг бот станет незаменимым инструментом для развития вашей команды и повышения эффективности менторинга!"
logging.basicConfig(level=logging.INFO)

# --------- DB------

# Подключение к базе данных (если файла базы данных не существует, он будет создан)
conn = sqlite3.connect('mentoring_bot.db')
cursor = conn.cursor()

# Создание таблицы Juns
cursor.execute('''
CREATE TABLE IF NOT EXISTS Juns (
    user_jun TEXT PRIMARY KEY,
    users_mentr TEXT,
    about_yourself TEXT,
    progress TEXT,
    zadachi TEXT,
    FOREIGN KEY (users_mentr) REFERENCES Mntrs(mentrs_username)
)
''')

# Создание таблицы Mntrs
cursor.execute('''
CREATE TABLE IF NOT EXISTS Mntrs (
    mentrs_username TEXT NOT NULL,
    about_of_mentr TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS workspace (
    workspace_name TEXT,
    workspace_ssilki TEXT,
    workspace_code INT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS baza_znanie (
    baza_znanie_name TEXT,
    baza_znanie_ssilki TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS admin (
    admin_username TEXT
)
''')

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()

print("База данных и таблицы успешно созданы.")

# ---------- DB ------

#------- Добавление в таблицу Mntrs ------

# Настройка базы данных
conn = sqlite3.connect('mentoring_bot.db')
cursor = conn.cursor()

# Определение состояний
class AddMentrStates(StatesGroup):
    waiting_for_username = State()

# Добавление ментров
async def add_mentr(message: types.Message, state: FSMContext):
    if message.from_user.username == admin_username:
        await message.answer("Введите username ментора")
        await state.set_state(AddMentrStates.waiting_for_username)
    else:
        await message.answer(message.from_user.username)
        await message.answer("Вы не админ")

# Добавление админа
def get_all_admins():
    cursor.execute('''
    SELECT admin_username FROM admin
    ''')
    rows = cursor.fetchall()
    return [row[0] for row in rows]

class AddAdminStates(StatesGroup):
    waiting_for_admin_username = State()

async def add_admin(message: types.Message, state: FSMContext):
    admins = get_all_admins()
    if message.from_user.username == admin_username or message.from_user.username in admins:
        await message.answer("Введите username нового админа:")
        await state.set_state(AddAdminStates.waiting_for_admin_username)
    else:
        await message.answer("Вы не админ")

async def process_admin_username(message: types.Message, state: FSMContext):
    new_admin_username = message.text
    new_admin_username = new_admin_username.replace("@", "")
    # Добавление нового админа в базу данных
    cursor.execute('''
    INSERT INTO admin (admin_username) VALUES (?)
    ''', (new_admin_username,))
    conn.commit()

    await message.answer(f"Админ {new_admin_username} успешно добавлен.")
    await state.clear()

async def get_admins(message: types.Message):
    admins = get_all_admins()
    await message.answer(f"Админы:\n {admins}")

# Авторизация
async def process_username(message: types.Message, state: FSMContext):
    username = message.text
    username = username.replace("@", "")
    cursor.execute('''
    INSERT INTO Mntrs (mentrs_username) VALUES (?)
    ''', (username,))
    conn.commit()
    await message.answer(f"Ментор {username} успешно добавлен.")
    await state.clear()

async def is_mentor (user_id: int)->bool:
    cursor.execute('''
    SELECT * FROM Mntrs WHERE mentrs_username = ?
    ''', (user_id,))
    return cursor.fetchone() is not None

async def is_jun (user_id: int)->bool:
    cursor.execute('''
    SELECT * FROM Juns WHERE user_jun = ?
    ''', (user_id,))
    return cursor.fetchone() is not None

# Добавление джуна
async def add_jun(message: types.Message, ssilka: str):
    username = message.from_user.username
    cursor.execute('''
    INSERT INTO Juns (user_jun, users_mentr) VALUES (?, ?)
    ''', (username, ssilka))
    conn.commit()
    await message.answer(f"Джун {username} успешно добавлен.")

# Получение всех менторов
async def get_all_mentors()-> list:
    cursor.execute('''
    SELECT * FROM Mntrs
    ''')
    mentors = cursor.fetchall()
    return [mentor[0] for mentor in mentors]

async def get_all_juns()-> list:
    cursor.execute('''
    SELECT * FROM Juns
    ''')
    juns = cursor.fetchall()
    return [jun[0] for jun in juns]

async def handler_start(message: types.Message, command: CommandStart):
    # Получение уникального кода из параметра start
    unique_code = command.args
    logging.info(f"Использован уникальный код:{unique_code}")
    mentors = await get_all_mentors()
    juns = await get_all_juns()

    if (unique_code and unique_code in mentors) or (message.from_user.username in mentors) or (message.from_user.username in juns):
        await message.answer(text=f"Вы использовали уникальную ссылку с кодом: {unique_code}")
        row = []
        if await is_mentor(message.from_user.username):
            await message.answer(text="Вы ментор")
            
            tg_channel_btn2 = InlineKeyboardButton(
            text="Далее",
            callback_data='mentor',
            )
            row.append(tg_channel_btn2)
        else:
            if await is_jun(message.from_user.username) == False:
                await message.answer("Вас нет в базе данных")
                await add_jun(message, unique_code)

            await message.answer(text="Вы джун")
            tg_channel_btn = InlineKeyboardButton(
            text="Далее",
            callback_data='jun',
            )
            row.append(tg_channel_btn)
        
        rows = [row]
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer(
            text=start_message2,
            reply_markup=markup,
        )
    else:
        await message.answer(text="Добро пожаловать! Вы не использовали уникальную ссылку.", reply_markup=ReplyKeyboardRemove())
# --------------------------Конец авторизации    
        

async def handler_ment(callback_query: CallbackQuery):
    continue_btn = InlineKeyboardButton(
        text="Продолжить",
        callback_data='continue_mentor',
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await callback_query.message.answer(message_for_mentr, reply_markup=markup)
    await callback_query.message.delete()  # Удаление сообщения
    await callback_query.answer()


async def handler_jun(callback_query: CallbackQuery):
    continue_btn = InlineKeyboardButton(
        text="Далее",
        callback_data='continue_jun',
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await callback_query.message.answer(message_for_jun, reply_markup=markup)
    await callback_query.message.delete()  # Удаление сообщения
    await callback_query.answer()

# ------------------------------------------------------------------------------
# Пространство Ментора

async def handler_continue_callback_mentor(callback_query: CallbackQuery):
    begin_button = InlineKeyboardButton(
        text="Начать",
        callback_data='begin_mentor',
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[ begin_button]])
    await callback_query.message.answer(welcome_mentor_message, reply_markup=markup)
    await callback_query.message.delete()
    await callback_query.answer()

async def handler_begin_mentor(callback_query: CallbackQuery):

    workspace_btn = KeyboardButton(
        text="Рабочее пространство"
    )
    ground_of_command_btn = KeyboardButton(
        text="пространство команды"
    )
    my_juns_btn = KeyboardButton(
        text="Мои джуны"
    )
    baza_znanie_btn = KeyboardButton(
        text="база знаний"
    )
    my_profile_btn = KeyboardButton(
        text="Мой Профиль"
    )
    about_of_bot_btn = KeyboardButton(
        text="О Боте"
    )
    
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [workspace_btn],
            [ground_of_command_btn],
            [my_juns_btn],
            [baza_znanie_btn],
            [my_profile_btn],
            [about_of_bot_btn],
        ],
        resize_keyboard=True
    )

    await callback_query.message.answer("Выберите действие из меню", reply_markup=markup)
    await callback_query.message.delete()
    await callback_query.answer()

async def handler_about_of_bot2(message: types.Message):
    continue_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    await message.answer("О боте", reply_markup=ReplyKeyboardRemove())
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await message.answer(messafe_about_of_bot, reply_markup=markup)


# ---------------------Профиль ментра и редактирование---------------
async def handler_my_profile_mentor(message: types.Message):
    back_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    edit_btn = InlineKeyboardButton(
        text="Редактировать",
        callback_data='edit_profile_mentor',
    )
    cursor.execute('''
    SELECT about_of_mentr FROM Mntrs WHERE mentrs_username = ?
    ''', (message.from_user.username,))
    result = cursor.fetchone()
    
    if result:
        about_of_mentr = result[0]
        profile_text = about_of_mentr
    else:
        profile_text = "Профиль не найден."

    await message.answer("Ваш профиль", reply_markup=ReplyKeyboardRemove())
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_btn, edit_btn]])
    await message.answer(profile_text, reply_markup=markup)

class EditProfileStates(StatesGroup):
    waiting_for_new_profile_text = State()
async def edit_profile_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите новый текст профиля:")
    await state.set_state(EditProfileStates.waiting_for_new_profile_text)
    await callback_query.answer()
async def process_new_profile_text(message: types.Message, state: FSMContext):
    new_profile_text = message.text
    username = message.from_user.username

    # Обновление базы данных
    cursor.execute('''
    UPDATE Mntrs SET about_of_mentr = ? WHERE mentrs_username = ?
    ''', (new_profile_text, username))
    conn.commit()

    await message.answer("Ваш профиль успешно обновлен.")
    await state.clear()

# ---------------------Конец Профиля ментра----------------------------


# ---------------------База Знаний ---------------------

class AddBazaZnanieStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_link = State()

async def baza_znanie_mentor(message: types.Message):
    back_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    add_btn = InlineKeyboardButton(
        text="Добавить ссылку",
        callback_data='add_baza_znanie',
    )
    # Извлечение данных из таблицы baza_znanie
    cursor.execute('''
    SELECT baza_znanie_name, baza_znanie_ssilki FROM baza_znanie
    ''')
    rows = cursor.fetchall()
    
    # Создание инлайн-кнопок для каждой строки
    buttons = []
    for row in rows:
        name, link = row
        buttons.append([InlineKeyboardButton(text=name, url=link)])
    
    # Добавление кнопки "Назад"
    buttons.append([back_btn])
    buttons.append([add_btn])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer("База знаний", reply_markup=ReplyKeyboardRemove()) 
    await message.answer("Выберите элемент базы знаний:", reply_markup=markup)

async def add_baza_znanie_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название для новой ссылки:")
    await state.set_state(AddBazaZnanieStates.waiting_for_name)
    await callback_query.answer()

async def process_baza_znanie_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(baza_znanie_name=name)
    await message.answer("Введите URL для новой ссылки:")
    await state.set_state(AddBazaZnanieStates.waiting_for_link)

async def process_baza_znanie_link(message: types.Message, state: FSMContext):
    back_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])
    link = message.text
    user_data = await state.get_data()
    name = user_data['baza_znanie_name']

    # Добавление новой записи в базу данных
    cursor.execute('''
    INSERT INTO baza_znanie (baza_znanie_name, baza_znanie_ssilki) VALUES (?, ?)
    ''', (name, link))
    conn.commit()

    await message.answer("Ссылка успешно добавлена.", reply_markup=markup)
    await state.clear()
# ---------------- Конец базы знаний----------------------------------

# -----------------джуны ментра----------------
async def juns_mentora(message: types.Message):
    back_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    add_jun_btn = KeyboardButton(
        text="Добавить джуна",
        callback_data='add_jun_ssilka',
    )
    username_mentor = message.from_user.username.replace("@", "")
    juns = await get_juns_by_mentor(username_mentor)
    keyboard = [[back_btn]]
    
    for jun in juns:
        keyboard.append([InlineKeyboardButton(text=f"@{jun}", callback_data=f'jun_info_{jun}')])
    await message.answer("Мои джуны", reply_markup=ReplyKeyboardRemove()) 

    keyboard_reply = ReplyKeyboardMarkup(keyboard=[[add_jun_btn]], resize_keyboard=True)
    await message.answer("Добавить джуна?", reply_markup=keyboard_reply)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Выберите джуна для действий", reply_markup=markup)
    

async def jun_info_handler(callback_query: CallbackQuery):
    jun_username = callback_query.data.split('_')[2]
    actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Просмотр прогресса", callback_data=f'view_progress_{jun_username}')],
        [InlineKeyboardButton(text="Посмотреть задачи", callback_data=f'view_tasks_{jun_username}')],
        [InlineKeyboardButton(text="Назначить задачу", callback_data=f'assign_task_{jun_username}')],
        [InlineKeyboardButton(text="Назад", callback_data='begin_mentor')]
    ])
    await callback_query.message.answer(f"Выберите действие для @{jun_username}", reply_markup=actions_keyboard)
    await callback_query.answer()

async def view_progress_handler(callback_query: CallbackQuery):
    jun_username = callback_query.data.split('_')[2]
    # Здесь добавьте логику для получения и отображения прогресса джуна
    cursor.execute('''
    SELECT progress FROM Juns WHERE user_jun = ?
    ''', (jun_username,))
    result = cursor.fetchone()
    progress = result[0] if result else "Прогресс не найден"

    await callback_query.message.answer(f"Прогресс @{jun_username}: {progress}")
    await callback_query.answer()

async def view_tasks_handler(callback_query: CallbackQuery):
    jun_username = callback_query.data.split('_')[2]
    # Здесь добавьте логику для получения и отображения задач джуна
    cursor.execute('''
    SELECT zadachi FROM Juns WHERE user_jun = ?
    ''', (jun_username,))
    result = cursor.fetchone()
    tasks = result[0] if result else "Задачи не найдены"
    await callback_query.message.answer(f"Задачи @{jun_username}:\n{tasks}")
    await callback_query.answer()

# --------------------------------------------Назнначение задачи
# Определение состояний
class AssignTaskStates(StatesGroup):
    waiting_for_task = State()

async def assign_task_handler(callback_query: CallbackQuery, state: FSMContext):
    jun_username = callback_query.data.split('_')[2]
    await callback_query.message.answer(f"Назначить задачу для @{jun_username}. Введите текст задачи:")
    await state.update_data(jun_username=jun_username)
    await state.set_state(AssignTaskStates.waiting_for_task)
    await callback_query.answer()

async def process_task_text(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    jun_username = user_data['jun_username']
    task_text = message.text

    # Получение текущих задач
    cursor.execute('''
    SELECT zadachi FROM Juns WHERE user_jun = ?
    ''', (jun_username,))
    result = cursor.fetchone()
    tasks = result[0] if result else ""

    updated_tasks = f"{tasks}\n- {task_text}"
    # Обновление базы данных
    cursor.execute('''
    UPDATE Juns SET zadachi = ? WHERE user_jun = ?
    ''', (updated_tasks, jun_username))
    conn.commit()

    await message.answer(f"Задача для @{jun_username} успешно добавлена.")
    await state.clear()


async def get_juns_by_mentor(mentor_username: str) -> list:
    cursor.execute('''
    SELECT user_jun FROM Juns WHERE users_mentr = ?
    ''', (mentor_username,))
    juns = cursor.fetchall()
    return [jun[0] for jun in juns]

async def add_jun_ssilka(message: types.Message):
    unic_code = message.from_user.username.replace("@", "")
    back_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    await message.answer(f"https://t.me/{bot_username}?start={unic_code}")
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])
    await message.answer("Отправьте ссылку для добавления джуна", reply_markup=markup)

# -------------------- Пространство команды---------------------
async def ground_of_team_mentor(message: types.Message):
    back_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    await message.answer("Пространство команды", reply_markup=ReplyKeyboardRemove()) 
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])
    await message.answer("Какое то пространство команды", reply_markup=markup)
# -------------------- Какой-то пространство команды---------------------

# --------------------Рабочее про-во ментра------------------------------
from random import randint
class CreateWorkspaceStates(StatesGroup):
    waiting_for_workspace_name = State()
    waiting_for_workspace_link = State()

async def workspace_mentor(message: types.Message): 
    back_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='begin_mentor',
    )
    start_workspace_btn = InlineKeyboardButton(
        text="Начать работу",
        callback_data='start_workspace',
    )
    keyboard = [[back_btn, start_workspace_btn]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(welcome_mentor_message, reply_markup=markup)

async def start_workspace_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название для нового рабочего пространства:")
    await state.set_state(CreateWorkspaceStates.waiting_for_workspace_name)
    await callback_query.answer()

async def process_workspace_name(message: types.Message, state: FSMContext):
    workspace_name = message.text
    await state.update_data(workspace_name=workspace_name)
    await message.answer("Введите ссылку для нового рабочего пространства:")
    await state.set_state(CreateWorkspaceStates.waiting_for_workspace_link)

async def process_workspace_link(message: types.Message, state: FSMContext):
    workspace_link = message.text
    user_data = await state.get_data()
    workspace_name = user_data['workspace_name']
    workspace_code = randint(0,1000)
    # Добавление новой записи в базу данных
    cursor.execute('''
    INSERT INTO workspace (workspace_name, workspace_ssilki, workspace_code) VALUES (?, ?, ?)
    ''', (workspace_name, workspace_link, workspace_code))
    conn.commit()

    await message.answer("Рабочее пространство успешно создано.")
    await message.answer(f"Код рабочего пространства: {workspace_code}")
    await state.clear()

# --------------------Конец про-ва --------------------------------------


# Конец пр-ва ментора
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Пространство Джуна
async def handler_continue_callback_jun(callback_query: CallbackQuery):
    ground_of_command_btn = KeyboardButton(
        text="Пространство команды"
    )
    baza_znanie_btn = KeyboardButton(
        text="База знаний"
    )
    svyz_s_mentron_btn = KeyboardButton(
        text="Связь с ментором"
    )
    my_profile_btn = KeyboardButton(
        text="Мой профиль"
    )
    about_of_bot_btn = KeyboardButton(
        text="О боте"
    )
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [ground_of_command_btn],
            [baza_znanie_btn],
            [svyz_s_mentron_btn],
            [my_profile_btn],
            [about_of_bot_btn]
        ],
        resize_keyboard=True
    )

    await callback_query.message.answer(ground_of_jun, reply_markup=markup)
    await callback_query.message.delete()
    await callback_query.answer()

async def handler_ground_of_command(message: types.Message):
    continue_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='continue_jun',
    )
    await message.answer("Пространство команды", reply_markup=ReplyKeyboardRemove())
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await message.answer("Какое то пространство команды", reply_markup=markup)

async def handler_baza_znanie(message: types.Message):
    continue_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='continue_jun',
    )
    await message.answer("База знаний", reply_markup=ReplyKeyboardRemove())
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await message.answer("Какая- то база знаний", reply_markup=markup)

async def handler_svyz_s_mentron(message: types.Message):
    continue_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='continue_jun',
    )
    await message.answer("Связь с ментором", reply_markup=ReplyKeyboardRemove())
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await message.answer("Что то там", reply_markup=markup)

async def handler_my_profile(message: types.Message):
    continue_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='continue_jun',
    )
    await message.answer("Мой профиль", reply_markup=ReplyKeyboardRemove())
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await message.answer("Ваш профиль", reply_markup=markup)


async def handler_about_of_bot(message: types.Message):
    continue_btn = InlineKeyboardButton(
        text="Назад",
        callback_data='continue_jun',
    )
    await message.answer("О боте", reply_markup=ReplyKeyboardRemove())
    markup = InlineKeyboardMarkup(inline_keyboard=[[continue_btn]])
    await message.answer(messafe_about_of_bot, reply_markup=markup)
    
# Конец пр-ва джуна
# ------------------------------------------------------------------------------



async def handler_start_callback(callback_query: CallbackQuery):
    await callback_query.message.delete()  # Удаление сообщения
    await handler_start(callback_query.message)

async def main():
    logging.info("Запуск бота")
    logging.basicConfig(level=logging.INFO)
    dp.message.register(handler_start, CommandStart())
    # Админская часть
    dp.message.register(add_mentr, Command("add_mentr"))
    dp.message.register(process_username, AddMentrStates.waiting_for_username)
    # Добавление админов
    dp.message.register(add_admin, Command("add_admin"))
    dp.message.register(process_admin_username, AddAdminStates.waiting_for_admin_username)
    dp.message.register(get_admins, Command("get_admins"))

    # Регистрация для ментра
    dp.callback_query.register(handler_ment, lambda c: c.data == 'mentor')
    # Регистрация для джуна
    dp.callback_query.register(handler_jun, lambda c: c.data == 'jun')
    # Регистрация начального меню
    dp.callback_query.register(handler_start_callback, lambda c: c.data == 'start')
    
    # Про-во джуна
    dp.callback_query.register(handler_continue_callback_jun, lambda c: c.data == 'continue_jun')
    # Регистрация пр-ва команды
    dp.message.register(handler_ground_of_command, lambda message: message.text == "Пространство команды")
    # Регистрация базы знаний
    dp.message.register(handler_baza_znanie, lambda message: message.text == "База знаний")
    # Регистрация связи с ментором
    dp.message.register(handler_svyz_s_mentron, lambda message: message.text == "Связь с ментором")
    # Регистрация профиля
    dp.message.register(handler_my_profile, lambda message: message.text == "Мой профиль")
    # Регистрация о боте
    dp.message.register(handler_about_of_bot, lambda message: message.text == "О боте")
    

    # Про-во ментора
    dp.callback_query.register(handler_continue_callback_mentor, lambda c: c.data == 'continue_mentor')
    # Пр-во метнтра
    dp.callback_query.register(handler_begin_mentor, lambda c: c.data == 'begin_mentor')
    # Приглашение джуна
    dp.message.register(add_jun_ssilka, lambda message: message.text == "Добавить джуна")
    # Действия над джуном
    dp.callback_query.register(jun_info_handler, lambda c: c.data.startswith('jun_info_'))
    dp.callback_query.register(view_progress_handler, lambda c: c.data.startswith('view_progress_'))
    dp.callback_query.register(view_tasks_handler, lambda c: c.data.startswith('view_tasks_'))  
    dp.callback_query.register(assign_task_handler, lambda c: c.data.startswith('assign_task_'))
    # Назначение задачи
    dp.callback_query.register(assign_task_handler, lambda c: c.data.startswith('assign_task_'))
    dp.message.register(process_task_text, AssignTaskStates.waiting_for_task)

    # Регистрация о боте для ментра
    dp.message.register(handler_about_of_bot2, lambda message: message.text == "О Боте")
    # Регистрация профиля ментора
    dp.message.register(handler_my_profile_mentor, lambda message: message.text == "Мой Профиль")
    # Редактирование профиля
    dp.callback_query.register(edit_profile_handler, lambda c: c.data == 'edit_profile_mentor')
    dp.message.register(process_new_profile_text, EditProfileStates.waiting_for_new_profile_text)
    # Регистрация редактирования ментра
    #dp.callback_query.register(handler_edit_profile_mentor, lambda c: c.data == 'edit_profile_mentor')
    # Регистрация базы знаний
    dp.message.register(baza_znanie_mentor, lambda message: message.text == "база знаний")
    # Добавление БЗ
    dp.callback_query.register(add_baza_znanie_handler, lambda c: c.data == 'add_baza_znanie')
    dp.message.register(process_baza_znanie_name, AddBazaZnanieStates.waiting_for_name)
    dp.message.register(process_baza_znanie_link, AddBazaZnanieStates.waiting_for_link)

    # Рабочее пр-во
    dp.message.register(workspace_mentor, lambda message: message.text == "Рабочее пространство")
    dp.callback_query.register(start_workspace_handler, lambda c: c.data == 'start_workspace')
    dp.message.register(process_workspace_name, CreateWorkspaceStates.waiting_for_workspace_name)
    dp.message.register(process_workspace_link, CreateWorkspaceStates.waiting_for_workspace_link)
    # Регистрация джунов
    dp.message.register(juns_mentora, lambda message: message.text == "Мои джуны")
    # Регистрация пространства команды
    dp.message.register(ground_of_team_mentor, lambda message: message.text == "пространство команды")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())