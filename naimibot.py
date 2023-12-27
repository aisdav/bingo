from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
import aiogram
import random
import tracemalloc
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.markdown import escape_md
tracemalloc.start()
API_TOKEN = '6871615330:AAHepR2mQz-OccsMXDL1sgS8NrTOFxQVqbA'
ADMIN_ID = '832892390'
admin_id = [832892390,6427864248,6037168719,5671880832,713104739,1581568237,5224223665]

collecting = False
class ClientState(StatesGroup):
    collecting_users = State()
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# Переменная для хранения списка участников
participants_list = []
random_num= []
pinned_message_id = None
total_numbers = []
typ= False

async def is_admin(user_id):
    # Здесь можно добавить дополнительную логику проверки на администратора
    return str(user_id) == ADMIN_ID


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.from_user.id not in admin_id:
        return
    global random_num,participants_list,total_numbers
    random_num = []
    participants_list= []
    total_numbers= []
    await message.reply("Старт игры 🎰

Для записи на игру отправьте свой @user_name и 5 чисел от 1 до 100:")


@dp.message_handler(commands=['bingo'])
async def start_game(message: types.Message, state: FSMContext):
    
    # Проверяем, является ли отправитель администратором
    if message.from_user.id not in admin_id:
        return
    try:
        await bot.unpin_chat_message(message.chat.id)
    except:
        pass
    global participants_list,collecting,random_num
    participants_list = []
    total_numbers = []
    random_num
    collecting = True
    # Отправляем сообщение "Открыта запись на игру"
    await message.reply("Открыта запись на игру. Участвовать могут все участники группы.\n"
                        "Пожалуйста, отправьте мне свои числа от 1 до 100 через пробел, например: @username 1 2 3 4 5")
@dp.message_handler(commands=['roullet'])
async def start_game(message: types.Message):
    global participants_list,typ,random_num
    # Проверяем, является ли отправитель администратором
    if message.from_user.id not in admin_id:
        return
    try:
        await bot.unpin_chat_message(message.chat.id)
    except:
        pass
    participants_list = []
    total_numbers = []
    random_num =[]
    typ = True
    # Отправляем сообщение "Открыта запись на игру"
    await message.reply("Открыта запись на игру. Участвовать могут все участники группы.\n"
                        "Пожалуйста, отправьте мне свой username.Например: @username")
@dp.message_handler(lambda message: message.text.startswith('@') and typ)
async def handle_participant_number(message: types.Message):
    global participants_list,typ
    if typ== True:
        username = message.text.split()[0]
        # Добавляем участника в список
        participants_list.append(username)
        # Обновляем закрепленное сообщение с участниками
        await send_participant_message(message.chat.id)   

@dp.message_handler(lambda message: message.text.startswith('@') and collecting)
async def handle_participants_numbers(message: types.Message):
    global participants_list,collecting
    if collecting== True:

        # Получаем информацию о пользователе
        user_id = message.from_user.id
        username = message.text.split()[0][1:]  # Извлекаем имя пользователя

        # Получаем числа от пользователя
        try:
            parts = message.text.split()
            username = parts[0][1:] if parts[0].startswith('@') else None
            numbers = [int(num) for num in parts[1:]]
            print(username,numbers)
            if len(numbers) != 5 or any(num < 1 or num > 100 for num in numbers):
                raise ValueError()
        except ValueError:
            await message.reply("Неправильный формат чисел. Пожалуйста, отправьте 5 чисел от 1 до 100.")
            return

        # Добавляем участника в список
        participants_list.append((username, numbers))

        # Обновляем закрепленное сообщение с участниками
        await send_participants_message(message.chat.id)
async def send_participant_message(chat_id):
    text = "📋Список участников:\n\n"
    for i, username in enumerate(participants_list, start=1):
        text += f"{i} {username}\n"
        if i < len(participants_list):  # Добавляем символ ➖ между записями, кроме последней
            text += "➖\n"
    print(participants_list)
    try:
        # Получаем ID предыдущего закрепленного сообщения
        chat = await bot.get_chat(chat_id)
        pinned_message_id = getattr(chat.pinned_message, 'message_id', None)

        if pinned_message_id:
            try:
                escaped_text = escape_md(text)
                await bot.edit_message_text(escaped_text, chat_id, pinned_message_id, parse_mode=ParseMode.MARKDOWN)
            except aiogram.utils.exceptions.MessageNotModified as e:
                if "Message is not modified" in str(e):
                        # Игнорировать ошибку "Message is not modified"
                    pass
                else:
                    # Обработка других исключений (если это не ошибка "Message is not modified")
                    print(f"Error: {e}")
        else:
            # Если нет предыдущего закрепленного сообщения, отправляем новое и закрепляем его
            try:
                escaped_text = escape_md(text)
                pinned_message = await bot.send_message(chat_id, escaped_text, parse_mode=ParseMode.MARKDOWN)
                await bot.pin_chat_message(chat_id, pinned_message.message_id)
            except Exception as e:
                print(f"Error while sending/pinning message: {e}")
    except Exception as e:
        print(f"Error while sending/pinning message: {e}")
async def send_participants_message(chat_id):
    global participants_list
    formatted_text = "📋Список участников:\n\n"

    for i, (username, numbers) in enumerate(participants_list, start=1):
        # Заменяем слеш перед цифрами в каждом числе
        numbers_str = ' '.join(map(lambda x: str(x).replace('/', ''), numbers))
        formatted_text += f"{i} @{username} {numbers_str}\n"
        if i < len(participants_list):  # Добавляем символ ➖ между записями, кроме последней
            formatted_text += "➖\n"

        # Получаем ID предыдущего закрепленного сообщения
    chat = await bot.get_chat(chat_id)
    pinned_message_id = getattr(chat.pinned_message, 'message_id', None)

        # Если есть предыдущее закрепленное сообщение, обновляем его текст
    if pinned_message_id:
        try:
            escaped_text = escape_md(formatted_text )
            # print(f"Current text: {escaped_text}")
            await bot.edit_message_text(escaped_text, chat_id, pinned_message_id, parse_mode=ParseMode.MARKDOWN)
        except aiogram.utils.exceptions.MessageNotModified as e:
            if "Message is not modified" in str(e):
                # Игнорировать ошибку "Message is not modified"
                pass
            else:
                # Обработка других исключений (если это не ошибка "Message is not modified")
                print(f"Error: {e}")
    else:
        # Если нет предыдущего закрепленного сообщения, отправляем новое и закрепляем его
        try:
            escaped_text = escape_md(formatted_text)
            print(escaped_text)
            pinned_message = await bot.send_message(chat_id, escaped_text, parse_mode=ParseMode.MARKDOWN)
            await bot.pin_chat_message(chat_id, pinned_message.message_id)
        except Exception as e:
            print(f"Error while sending/pinning message: {e}")
    



@dp.message_handler(lambda message: message.text == "/stop" and collecting)
async def stop_game(message: types.Message):
    # Проверяем, является ли отправитель администратором
    if message.from_user.id not in admin_id:
        return
    global total_numbers,collecting,random_num
    random_num =[]
    total_numbers = []
    collecting = False
    # Сбрасываем список участников и удаляем закрепленное сообщение
    global participants_list
    participants_list = []
    try:
        await bot.unpin_chat_message(chat_id=message.chat.id)
    except:
        pass
    await bot.send_message(message.chat.id, "Список закрыт.")
@dp.message_handler(lambda message: message.text == "/over" and typ)
async def over_game(message: types.Message):
    global typ,participants_list,random_num
    total_numbers = []
    random_num= []
    typ = False
    # Проверяем, является ли отправитель администратором
    if message.from_user.id not in admin_id:
        return
    # Сбрасываем список участников и удаляем закрепленное сообщение
    global participants_list
    await send_participant_message(message.chat.id)
    participants_list = []
    await bot.send_message(message.chat.id, "Список закрыт.")
    await bot.unpin_chat_message(chat_id=message.chat.id)
    pinned_message_id = 0 
@dp.message_handler(commands=['random'])
async def generate_random(message: types.Message):
    global typ, participants

    # Проверяем, является ли отправитель администратором
    if message.from_user.id not in admin_id:
        return

    if typ:
        await message.answer("Сначала завершите сбор участников командой /over.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) == 3:
            _, start_range, end_range = command_parts
            start_range, end_range= int(start_range), int(end_range)
        else:
            raise ValueError()
    except (ValueError, IndexError):
        await message.answer("Неверный формат команды. Используйте /random start_range end_range.")
        return

    # Генерируем случайные числа в указанном диапазоне
    random_number = random.sample(range(start_range, end_range + 1), 1)
    
    random_num.extend(random_number)
    # Отправляем результат
    print(random_num)
    await message.answer(f"🎲 ᴘɪʀᴀᴛᴇs ᴋᴢ ʀᴏᴜʟʟᴇᴛ\n\n" + "\n➖\n".join(map(str, random_num)))
@dp.message_handler(commands=['number'])
async def generate_numbers(message: types.Message):
    global random_num
   # Проверяем, является ли отправитель администратором
    if message.from_user.id not in admin_id:
        return
    random_num = []
    try:
        # Получаем ID предыдущего закрепленного сообщения
        chat = await bot.get_chat(message.chat.id)
        pinned_message_id = getattr(chat.pinned_message, 'message_id', None)
    except Exception as e:
        pass
        pinned_message_id = None

    # Генерируем 5 рандомных чисел от 1 до 100
    random_numbers = random.sample(range(1, 101), 5)
    # Создаем новый список с добавленными элементами
    new_element = '➖'
    new_list = []
    for item in random_numbers:
        new_list.append(item)
        new_list.append(new_element)
    # Убираем последний лишний добавленный элемент
    new_list.pop()
    total_numbers.extend(new_list)
    total_numbers.append('\n')

    # Если есть предыдущее закрепленное сообщение, дополняем его
    if pinned_message_id:
        try:
            existing_message = await bot.edit_message_text(chat_id=message.chat.id,
                                                            message_id=pinned_message_id,
                                                            text=f"🎰 ᴘɪʀᴀᴛᴇs ᴋᴢ ʙɪɴɢᴏ:\n\n{''.join(map(str, total_numbers))}")
        except Exception as e:
            print(f"Error while editing pinned message: {e}")
    else:
        # Если нет предыдущего закрепленного сообщения, создаем новое
        try:
            message_text = f"🎰 ᴘɪʀᴀᴛᴇs ᴋᴢ ʙɪɴɢᴏ:\n\n {''.join(map(str, total_numbers))}"
            escaped_text = escape_md(message_text)
            existing_message = await bot.send_message(message.chat.id, escaped_text, parse_mode=ParseMode.MARKDOWN)
            await bot.pin_chat_message(message.chat.id, existing_message.message_id)
        except Exception as e:
            print(f"Error while sending/pinning message: {e}")


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
