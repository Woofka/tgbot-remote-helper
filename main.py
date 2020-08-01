import logging
import threading

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

from config import BOT_TOKEN, ALLOWED_IDS, MAIN_MAC
from bot_utils import mac_bytes_to_str, parse_mac_addr, wake_on_lan, ask_status, ask_uptime, protocol_handler,\
    status_observer


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='log.txt',
    level=logging.INFO
)


bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    logging.info(f'Command \"/start\" from user {message.from_user.id}')
    await message.answer("[WorkInProgress] Start")


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    logging.info(f'Command \"/help\" from user {message.from_user.id}')
    await message.answer("[WorkInProgress] Help")


@dp.message_handler(commands='settings')
async def cmd_settings(message: types.Message):
    logging.info(f'Command \"/settings\" from user {message.from_user.id}')
    await message.answer("[WorkInProgress] Settings")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    logging.info(f'Command \"/cancel\" from user {message.from_user.id}')

    current_state = await state.get_state()
    if current_state is None:
        await message.answer('No active command to cancel')
        return

    logging.info(f'Cancelling state {current_state}')
    await state.finish()
    await message.answer('Cancelled. Anything else I can do for you?', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands='wakeonlan')
async def cmd_wakeonlan(message: types.Message):
    logging.info(f'Command \"/wakeonlan\" from user {message.from_user.id}')

    if message.from_user.id not in ALLOWED_IDS:
        await message.answer('Sorry. You have no permission to use this command')
        return

    wake_on_lan(MAIN_MAC)
    await message.answer(
        md.text('Wake\-on\-LAN packet was sent to', md.code(MAIN_MAC)),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@dp.message_handler(commands='uptime')
async def cmd_uptime(message: types.Message):
    logging.info(f'Command \"/uptime\" from user {message.from_user.id}')

    if message.from_user.id not in ALLOWED_IDS:
        await message.answer('Sorry. You have no permission to use this command')
        return

    if not ask_uptime(MAIN_MAC, message.from_user.id):
        await message.answer(
            md.text('Device', md.code(MAIN_MAC), 'is not available now'),
            parse_mode=ParseMode.MARKDOWN_V2
        )


@dp.message_handler(commands='status')
async def cmd_status(message: types.Message):
    logging.info(f'Command \"/status\" from user {message.from_user.id}')

    if message.from_user.id not in ALLOWED_IDS:
        await message.answer('Sorry. You have no permission to use this command')
        return

    if not ask_status(MAIN_MAC, message.from_user.id):
        await message.answer(
            md.text('Device', md.code(MAIN_MAC), 'is not available now'),
            parse_mode=ParseMode.MARKDOWN_V2
        )


if __name__ == '__main__':
    th_protocol_handler = threading.Thread(target=protocol_handler)
    th_status_observer = threading.Thread(target=status_observer)
    th_protocol_handler.start()
    th_status_observer.start()
    executor.start_polling(dp, skip_updates=True)
