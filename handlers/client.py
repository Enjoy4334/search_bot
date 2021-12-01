import asyncio
import sqlite3
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hide_link
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.olx_db import sql_add_link, sql_read_olx_link, sql_remove_olx_link
from db.ria_db import sql_add_link_to_ria, sql_read_ria_link, sql_remove_ria_link
from create_bot import dp
from keyboards import kb_client
from keyboards import kb_client_auto
from keyboards import choose_parsers
from parsers import sql_output_olx_link, olx, sql_output_ria_link, auto_ria

run = True


class FsmCreateLinkOlx(StatesGroup):
    create = State()


class FsmCreateLinkAuto(StatesGroup):
    create_auto = State()


class FsmRemoveLink(StatesGroup):
    remove = State()


class FsmMyLinks(StatesGroup):
    show_links = State()


class FsmCancel(StatesGroup):
    cancel = State()


async def command_start(message: types.Message):
    await message.answer("""
1.Найдите интересующий вас товар на сайте OLX.UA 💎📷💍🚗, по выгодной вам цене💵 
2.Нажмите в панели ,создать ссылку 📎📎📎 
Вы  можете использовать мобильную версию браузера 
пример ссылки : [ https://m.olx.ua/nedvizhimost/ ]
🚨Внимание🚨
Для наиболее качественного результата ИСПОЛЬЗУЙТЕ 
     📍полную версию📍сайта OLX  в браузере 🚨Chrome🚨
Пример ссылки : [ https://www.olx.ua/uk/nedvizhimost/kvartiry-komnaty/prodazha-kvartir-komnat/ko/?search ]
🚨Смотреть ВИДЕО ИНСТРУКЦИЮ
3.Скопируйте ссылку интересующего вас фильтра в бота 💾 💾💾
4. Как только объявление по вашим критериям появится на сайте OLX.ua - вы получите уведомление первым!👍🏻 💵💶💷

🔑🔑🔑Что бы добавить дополнительную ссылку напишите администратору ✍🏻✍🏻✍🏻

🚨🚨🚨Внимание смотреть ВИДЕО ИНСТРУКЦИЮ для Android🚨🚨🚨
https://youtu.be/uxImf35UNUE
🚨🚨🚨Внимание смотреть ВИДЕО ИНСТРУКЦИЮ для  IPhone🚨🚨🚨
https://youtu.be/8tOxQjOZ0Kg""", reply_markup=choose_parsers,)
    await message.answer('Выберите агрегатор')


async def cancel_btn(message: types.Message, state: FSMContext):
    global run
    run = False

    await state.reset_state()
    await message.reply('Вернулись к выбору агрегатора', reply_markup=choose_parsers)


async def start_olx(message: types.Message):
    global run
    run = True
    await message.answer('Выберите опцию', reply_markup=kb_client)


async def start_create_link_olx(message: types.Message):
    await message.reply('Введите ссылку:')
    await FsmCreateLinkOlx.create.set()


async def link_invalid_olx(message: types.Message):
    await message.answer("""🚨Внимание смотреть видео инструкцию для IPhone 🚨https://youtu.be/8tOxQjOZ0Kg
🚨Внимание смотреть ВИДЕО ИНСТРУКЦИЮ для Android 🚨
https://youtu.be/uxImf35UNUE
1.Откоройте сайт OLX.ua📌 и найдите интересующий вас товар или услугу по интересующим вас фильтрам 🚗📱💎
Вы  можете использовать мобильную версию браузера 
пример ссылки : [ https://m.olx.ua/nedvizhimost/ ]
🚨Внимание🚨
Для наиболее качественного результата ИСПОЛЬЗУЙТЕ 
     📍полную версию📍сайта OLX  в браузере 🚨Chrome🚨
Пример ссылки : [ https://www.olx.ua/uk/nedvizhimost/kvartiry-komnaty/prodazha-kvartir-komnat/ko/?search ]
2.Скопируйте ссылку с сайта OLX.ua 💾💾💾
3.Вставьте ссылку сюда ⬇️⬇️⬇️
🔑🔑🔑Что бы добавить дополнительную ссылку напишите администратору @Brookland✍🏻✍🏻✍🏻""")


async def create_link_olx(message: types.Message, state: FSMContext):
    global run
    async with state.proxy() as url:
        url['url_olx'] = message.text
    await sql_add_link(state)
    data_res = []
    # tmp = json.dumps(data_res)

    while run:

        if not run:
            await state.finish()
            await cancel_btn(message, state)
            break
        else:

            url_for_olx = sql_output_olx_link()
            result_olx = olx(url=url_for_olx)

            if result_olx in data_res:
                url_for_olx = sql_output_olx_link()
                result_olx = olx(url=url_for_olx)

            if result_olx not in data_res:
                data_res.append(result_olx)
                parse_items = f'{hide_link(result_olx[1])} ' \
                              f'\n{hbold("Местоположение", ": ")}{result_olx[2]}' \
                              f'\n{hbold("Наименование", ": ")}{result_olx[3]}' \
                              f'\n{hbold("Цена", ": ")}{result_olx[4]}' \
                              f'\n{hide_link(result_olx[1])}'

                inline_kb_olx = InlineKeyboardMarkup()
                inline_kb_olx.add(InlineKeyboardButton('Перейти по ссылке', url=result_olx[5]))

                await message.answer(parse_items, parse_mode="HTML", reply_markup=inline_kb_olx)
        await asyncio.sleep(1)


async def show_links_olx(message: types.Message):
    read = await sql_read_olx_link()
    for link in read:
        await message.answer(str(link).strip("('").strip("')").strip(",").strip("'"))


async def removing_link_olx(message: types.Message):
    await sql_remove_olx_link()
    await message.answer('Ссылки удалены')


async def start_autoria(message: types.Message):
    global run
    run = True
    await message.answer('Выберите опцию', reply_markup=kb_client_auto)


async def start_create_link_autoria(message: types.Message):
    await message.reply('Введите ссылку:')
    await FsmCreateLinkAuto.create_auto.set()


async def link_invalid_autoria(message: types.Message):
    await message.answer("""🚨Внимание смотреть видео инструкцию для IPhone 🚨https://youtu.be/8tOxQjOZ0Kg
🚨Внимание смотреть ВИДЕО ИНСТРУКЦИЮ для Android 🚨
https://youtu.be/uxImf35UNUE
1.Откоройте сайт OLX.ua📌 и найдите интересующий вас товар или услугу по интересующим вас фильтрам 🚗📱💎
Вы  можете использовать мобильную версию браузера 
пример ссылки : [ https://m.olx.ua/nedvizhimost/ ]
🚨Внимание🚨
Для наиболее качественного результата ИСПОЛЬЗУЙТЕ 
     📍полную версию📍сайта OLX  в браузере 🚨Chrome🚨
Пример ссылки : 
[ https://www.olx.ua/uk/nedvizhimost/kvartiry-komnaty/prodazha-kvartir-komnat/ko/?search ]
2.Скопируйте ссылку с сайта OLX.ua 💾💾💾
3.Вставьте ссылку сюда ⬇️⬇️⬇️
🔑🔑🔑Что бы добавить дополнительную ссылку напишите администратору @Brookland✍🏻✍🏻✍🏻""")


async def create_link_autoria(message: types.Message, state: FSMContext):
    global run
    async with state.proxy() as url:
        url['url_autoria'] = message.text
    await sql_add_link_to_ria(state)
    data_res_ria = []

    while run:

        if not run:
            await state.finish()
            await cancel_btn(message, state)
            break
        else:

            url_for_ria = sql_output_ria_link()
            result_ria = auto_ria(url=url_for_ria)

            if result_ria in data_res_ria:
                url_for_ria = sql_output_ria_link()
                result_ria = auto_ria(url=url_for_ria)

            if result_ria not in data_res_ria:
                data_res_ria.append(result_ria)

                parse_items = f'{hide_link(result_ria[1])} ' \
                              f'\n{hbold("Местоположение", ": ")}{result_ria[2]}' \
                              f'\n{hbold("Наименование", ": ")}{result_ria[3]}' \
                              f'\n{hbold("Цена", ": ")}{result_ria[4]}' \
                              f'\n{hide_link(result_ria[1])}'

                inline_kb_ria = InlineKeyboardMarkup()
                inline_kb_ria.add(InlineKeyboardButton('Перейти по ссылке', url=result_ria[5]))

                await message.answer(parse_items, parse_mode="HTML", reply_markup=inline_kb_ria)
        await asyncio.sleep(1)


async def show_links_autoria(message: types.Message, state: FSMContext):
    read = await sql_read_ria_link()
    for link in read:
        await message.answer(str(link).strip("('").strip("')").strip(",").strip("'"))


async def removing_link_ria(message: types.Message):
    await sql_remove_ria_link()
    await message.answer('Ссылки удалены')


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'], content_types=['text'], state=None)
    dp.register_message_handler(cancel_btn, Text(equals='Вернуться к агрегаторам'), state='*')
    dp.register_message_handler(start_olx, Text('Olx'), content_types=['text'])
    dp.register_message_handler(start_create_link_olx, Text('Создать ссылку Olx'), state=None)
    dp.register_message_handler(link_invalid_olx, lambda message: 'https://www.olx.ua/' not in message.text,
                                state=FsmCreateLinkOlx.create)
    dp.register_message_handler(create_link_olx, content_types=['text'], state=FsmCreateLinkOlx.create)
    dp.register_message_handler(show_links_olx, Text(equals='Мои ссылки'))
    dp.register_message_handler(removing_link_olx, Text('Удалить ссылки Olx'))
    dp.register_message_handler(start_autoria, Text('Auto.ria'), content_types=['text'])
    dp.register_message_handler(start_create_link_autoria, Text('Создать ссылку Auto.ria'), state=None)
    dp.register_message_handler(link_invalid_autoria, lambda message: 'https://auto.ria.com/' not in message.text,
                                state=FsmCreateLinkAuto.create_auto)
    dp.register_message_handler(create_link_autoria, content_types=['text'], state=FsmCreateLinkAuto.create_auto)
    dp.register_message_handler(show_links_autoria, Text(equals='Мои ссылки с Auto.ria'))
    dp.register_message_handler(removing_link_ria, Text('Удалить ссылки Auto.ria'))
