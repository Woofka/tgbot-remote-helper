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
async def cmd_start(message: types.Message):
    logging.info(f'Command \"/help\" from user {message.from_user.id}')
    await message.answer("[WIP] Help")


@dp.message_handler(commands='settings')
async def cmd_start(message: types.Message):
    logging.info(f'Command \"/settings\" from user {message.from_user.id}')
    await message.answer("[WIP] Settings")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    logging.info(f'Command \"/cancel\" from user {message.from_user.id}')

    current_state = await state.get_state()
    if current_state is None:
        await message.answer('No active command to cancel')
        return

    logging.info(f'Cancelling state {current_state}')
    await state.finish()
    await message.answer('Cancelled. Anything else I can do for you?', reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
