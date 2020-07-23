import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

from config import BOT_TOKEN, ALLOWED_IDS
from bot_utils import *


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
    await message.answer("[WIP] Start")


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    logging.info(f'Command \"/help\" from user {message.from_user.id}')
    await message.answer("[WIP] Help")


@dp.message_handler(commands='settings')
async def cmd_settings(message: types.Message):
    logging.info(f'Command \"/settings\" from user {message.from_user.id}')
    await message.answer("[WIP] Settings")


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

    cmd_args = message.get_args()
    if cmd_args != '' and len(cmd_args) <= 20:
        mac = parse_mac_addr(cmd_args)
        if mac is not None:
            wake_on_lan(mac)
            await message.answer(
                md.text('Wake\-on\-LAN packet were sent to', md.code(mac_bytes_to_str(mac))),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

    await message.answer(
        md.text(
            md.text('To use Wake\-on\-LAN send me next message:'),
            md.code('/wakeonlan <mac>'),
            md.text('Where `<mac>` is MAC address of computer you want to turn on\.'),
            md.text('MAC should be written in one of the following ways:'),
            md.text('\-', md.code('11:22:33:aa:bb:cc')),
            md.text('\-', md.code('11.22.33.aa.bb.cc')),
            md.text('\-', md.code('11-22-33-aa-bb-cc')),
            sep='\n'
        ),
        parse_mode=ParseMode.MARKDOWN_V2
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
