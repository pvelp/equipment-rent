from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from bot.core.keyboards.utils import create_buttons
from bot.core.keyboards.cancel_keyboard import cancel, cancel_send_phone, CancelBtnName
from bot.core.db.actions import get_client_by_tg_id, add_client
from bot.core.states.user_state import UserState, Registration
from bot.core.keyboards.default_keyboard import default_kb
from bot.core.keyboards.user_keyboard import main_menu_kb, MainMenuBtnName
from bot.config import bot


async def start_command(message: types.Message):
    user = get_client_by_tg_id(message.from_user.id)
    if user is None:
        kb = create_buttons(["Зарегистрироваться"])
        await message.answer("Пройдите регистрацию", reply_markup=kb)
        await UserState.sign_up.set()
    else:
        await message.answer("Рады снова вас видеть")


async def sign_up_start_stage(message: types.Message):
    msg = message.text
    if msg == "Зарегистрироваться":
        await message.answer("*Шаг [1/3]*\nВведите вашe имя",
                             reply_markup=cancel(),
                             parse_mode="Markdown")
        await Registration.name_stage.set()
    elif msg == CancelBtnName.cancel_btn:
        await message.answer("Вы отменили регистрацию",  reply_markup=default_kb())
        await UserState.default_state.set()


async def sign_up_name_stage(message: types.Message, state: FSMContext):
    msg = message.text
    if msg == CancelBtnName.cancel_btn:
        await message.answer("Вы отменили регистрацию", reply_markup=default_kb())
        await UserState.default_state.set()
        await state.reset_data()
    else:
        await message.answer("*Шаг [2/3]*\nВведите дату вашего рождения",
                             reply_markup=cancel(),
                             parse_mode="Markdown")
        await state.update_data(name=msg)
        await state.update_data(nickname=message.from_user.username)
        await state.update_data(telegram_id=message.from_user.id)
        await Registration.birthday_stage.set()


async def sign_up_bday_stage(message: types.Message, state: FSMContext):
    msg = message.text
    if msg == CancelBtnName.cancel_btn:
        await message.answer("Вы отменили регистрацию", reply_markup=default_kb())
        await UserState.default_state.set()
        await state.reset_data()
    else:
        await message.answer("*Шаг [3/3]*\nПоделитесь номером телефона",
                             reply_markup=cancel_send_phone(),
                             parse_mode="Markdown")
        await state.update_data(bday=msg)
        await Registration.phone_stage.set()


async def cancel_sign_up_phone_stage(message: types.Message, state: FSMContext):
    msg = message.text
    if msg == CancelBtnName.cancel_btn:
        await message.answer("Вы отменили регистрацию", reply_markup=default_kb())
        await UserState.default_state.set()
        await state.reset_data()


async def sign_up_phone_stage(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Вы прошли регистрацию", reply_markup=main_menu_kb())
    await UserState.start.set()
    data = await state.get_data()
    add_client(data)
    await state.reset_data()


async def main_menu_handler(message: types.Message):
    msg = message.text
    if msg == MainMenuBtnName.menu:
        pass
    elif msg == MainMenuBtnName.tips:
        pass
    elif msg == MainMenuBtnName.sales:
        pass
    elif msg == MainMenuBtnName.events:
        pass
    elif msg == MainMenuBtnName.photos:
        pass
    elif msg == MainMenuBtnName.contacts:
        pass
    elif msg == MainMenuBtnName.feedback:
        pass
    elif msg == MainMenuBtnName.loyalty_program:
        pass


def register_users_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'], state=["*"])
    dp.register_message_handler(sign_up_start_stage, state=UserState.sign_up)
    dp.register_message_handler(sign_up_name_stage, state=Registration.name_stage)
    dp.register_message_handler(sign_up_bday_stage, state=Registration.birthday_stage)
    dp.register_message_handler(cancel_sign_up_phone_stage, state=Registration.phone_stage)
    dp.register_message_handler(sign_up_phone_stage, state=Registration.phone_stage,
                                content_types=types.ContentType.CONTACT)
    dp.register_message_handler(main_menu_handler, state=UserState.start)
