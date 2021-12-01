from aiogram import types, Dispatcher
from create_bot import dp


async def echo_sent(message: types.Message):
    await message.answer(message.text)


def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(echo_sent)
