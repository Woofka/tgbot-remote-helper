import logging
import asyncio
import datetime

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

from logger import setup_logger
from config import BOT_TOKEN, ALLOWED_IDS, MAC
from bot_utils import wake_on_lan, ask_uptime, protocol_handler, status_observer, get_last_status, get_wan_ip


setup_logger()
log = logging.getLogger('logger')


bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    log.info(f'Command \"/start\" from user {message.from_user.id}')
    await message.answer("[WorkInProgress] Start")


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    log.info(f'Command \"/help\" from user {message.from_user.id}')
    await message.answer("[WorkInProgress] Help")


@dp.message_handler(commands='settings')
async def cmd_settings(message: types.Message):
    log.info(f'Command \"/settings\" from user {message.from_user.id}')
    await message.answer("[WorkInProgress] Settings")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    log.info(f'Command \"/cancel\" from user {message.from_user.id}')

    current_state = await state.get_state()
    if current_state is None:
        await message.answer('No active command to cancel')
        return

    log.info(f'Cancelling state {current_state}')
    await state.finish()
    await message.answer('Cancelled. Anything else I can do for you?', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands='wakeonlan')
async def cmd_wakeonlan(message: types.Message):
    log.info(f'Command \"/wakeonlan\" from user {message.from_user.id}')

    if message.from_user.id not in ALLOWED_IDS:
        await message.answer('Sorry. You have no permission to use this command')
        return

    status, _ = get_last_status()
    if not status:
        wake_on_lan()
        await message.answer('Wake-on-LAN packet was sent')
    else:
        await message.answer('Device is already online')


@dp.message_handler(commands='uptime')
async def cmd_uptime(message: types.Message):
    log.info(f'Command \"/uptime\" from user {message.from_user.id}')

    if message.from_user.id not in ALLOWED_IDS:
        await message.answer('Sorry. You have no permission to use this command')
        return

    status, _ = get_last_status()
    if status:
        ask_uptime(message.from_user.id, message.chat.id)
    else:
        await message.answer('Device is offline')


@dp.message_handler(commands='status')
async def cmd_status(message: types.Message):
    log.info(f'Command \"/status\" from user {message.from_user.id}')

    if message.from_user.id not in ALLOWED_IDS:
        await message.answer('Sorry. You have no permission to use this command')
        return

    status, time = get_last_status()
    info = 'ONLINE' if status else 'OFFLINE'
    time = datetime.datetime.fromtimestamp(time).__format__('%H:%M:%S  %d %h %Y')
    await message.answer(f'Last known status  -  {info}  -  {time}')


@dp.message_handler(commands='wanip')
async def cmd_wanip(message: types.Message):
    log.info(f'Command \"/wanip\" from user {message.from_user.id}')

    if message.from_user.id not in ALLOWED_IDS:
        await message.answer('Sorry. You have no permission to use this command')
        return

    ip = get_wan_ip()
    await message.answer(
        md.text('Your WAN IP address  \- ', md.code(ip)),
        parse_mode=ParseMode.MARKDOWN_V2
    )


if __name__ == '__main__':
    log.info('Starting protocol handler')
    asyncio.ensure_future(protocol_handler(bot))
    log.info('Starting status observer')
    asyncio.ensure_future(status_observer(bot))
    log.info('Starting bot')
    executor.start_polling(dp, skip_updates=True)
