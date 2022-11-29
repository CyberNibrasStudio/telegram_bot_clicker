import asyncio
import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from config_reader import config
from datetime import date
import random
from db import BotDB
import requests
import json

QIWI_TOKEN = f'{config.qiwi_token.get_secret_value()}'
QIWI_ACCOUNT = f'{config.qiwi_account.get_secret_value()}'

s = requests.Session()
s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN  
parameters = {'rows': '50'}
h = s.get('https://edge.qiwi.com/payment-history/v1/persons/'+ QIWI_ACCOUNT +'/payments', params = parameters)
req = json.loads(h.text)


storage = MemoryStorage()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value())
# Диспетчер
dp = Dispatcher(bot, storage=storage)

BotDB = BotDB('accounts.db')

class Form(StatesGroup):
    gold = State()
    nameGame = State() 
    nameSkin = State()
    
class Form2(StatesGroup):
  money = State()

# Хэндлер на команду /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
  if (not BotDB.user_exists(message.from_user.id)):
    BotDB.add_user(message.from_user.id, 0.0001257, 0, 0)
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
  start = types.KeyboardButton('начать')
  upgrade = types.KeyboardButton('улучшения')
  balance = types.KeyboardButton('баланс')
  vivod = types.KeyboardButton('вывод')
  morebot = types.KeyboardButton('другие боты')
  markup.add(start, upgrade, balance, vivod, morebot)
  await message.answer("Hello!", reply_markup=markup)
  
  
@dp.message_handler()
async def get_user_message(msg: types.Message):
  if msg.text == "начать":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    click = types.KeyboardButton('клик')
    main = types.KeyboardButton('главное меню')
    markup.add(click, main)
    await bot.send_message(msg.from_user.id, "теперь нажимай на кнопку: клик", reply_markup=markup)
  elif msg.text == "главное меню":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    start = types.KeyboardButton('начать')
    upgrade = types.KeyboardButton('улучшения')
    balance = types.KeyboardButton('баланс')
    vivod = types.KeyboardButton('вывод')
    morebot = types.KeyboardButton('другие боты')
    markup.add(start, upgrade, balance, vivod, morebot)
    await bot.send_message(msg.from_user.id, "главное меню:", reply_markup=markup)
  elif msg.text == "баланс":
    markup = types.InlineKeyboardMarkup()
    pay = types.InlineKeyboardButton('пополнить баланс', callback_data="pay_pay")
    markup.add(pay)
    money = float(BotDB.get_records(msg.from_user.id)[3])
    moneyR = BotDB.get_records(msg.from_user.id)[4]
    await bot.send_message(msg.from_user.id, f"Голды: {round(money, 7)}, рублей: {moneyR}", reply_markup=markup)
  elif msg.text == "клик":
    result = BotDB.get_records(msg.from_user.id)
    plusmoney = float(result[2])
    money = float(result[3])
    money = money + plusmoney
    BotDB.update_money(msg.from_user.id, money)
    await bot.send_message(msg.from_user.id, f"☑️ вам зачислено +{plusmoney} голды")
  elif msg.text == "улучшения":
    markup = types.InlineKeyboardMarkup()
    one = types.InlineKeyboardButton("1", callback_data="one_upgrade")
    two = types.InlineKeyboardButton("2", callback_data="two_upgrade")
    markup.add(one, two)
    await bot.send_message(msg.from_user.id, "Выбери номер улучшения:\n1.Улучшить количество голды за клик.\nСтоимость 1 рубль.\n\n2.Пассивный доход 1 голда в час\nСтоимость 10 рублей", reply_markup=markup)
  elif msg.text == "вывод":
    result = BotDB.get_records(msg.from_user.id)
    money = int(result[3])
    if money < 10:
      await bot.send_message(msg.from_user.id, "для вывода надо не меньше 10 голды")
    else:
      await Form.gold.set()
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
      main = types.KeyboardButton('/cancel')
      markup.add(main)
      await bot.send_message(msg.chat.id, "Введи количество голды. Минимум для вывода 10 голды", reply_markup=markup)
  elif msg.text == "проверить оплату":
    error = 0
    payment = "не оплачено"
    result = BotDB.get_payments(msg.chat.id, payment)
    sum = result[2]
    comment = result[4]
    for i in range(len(req['data'])):
      if req['data'][i]['comment'] == comment:
        if req['data'][i]['sum']['amount'] == sum:
          money = BotDB.get_records(msg.chat.id)[2]
          money = money + sum
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
          mainmenu = types.KeyboardButton('главное меню')
          markup.add(mainmenu)
          BotDB.delete_payments(msg.chat.id, comment)
          BotDB.update_records(msg.chat.id, money)
          await bot.send_message(msg.chat.id, "оплата прошла успешно", reply_markup=markup)
      else:
        error = 1
    if error == 1:
      await bot.send_message(msg.chat.id, "вы не оплатили или оплата не прошла подождите пару минут и нажмите снова")
  elif msg.text == "отмена оплаты":
	  result = BotDB.get_payments(msg.chat.id, "не оплачено")
	  sum = result[2]
	  comment = result[4]
	  BotDB.delete_payments(msg.chat.id, comment)
	  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	  start = types.KeyboardButton('начать')
	  upgrade = types.KeyboardButton('улучшения')
	  balance = types.KeyboardButton('баланс')
	  vivod = types.KeyboardButton('вывод')
	  morebot = types.KeyboardButton('другие боты')
	  markup.add(start, upgrade, balance, vivod, morebot)
	  await bot.send_message(msg.from_user.id, "оплата отменена:", reply_markup=markup)
      
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ok')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    start = types.KeyboardButton('начать')
    upgrade = types.KeyboardButton('улучшения')
    balance = types.KeyboardButton('баланс')
    vivod = types.KeyboardButton('вывод')
    morebot = types.KeyboardButton('другие боты')
    markup.add(start, upgrade, balance, vivod, morebot)
    await bot.send_message(message.from_user.id, "главное меню:", reply_markup=markup)
    
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.gold)
async def process_age_invalid(message: types.Message):
    return await message.reply("напиши цифрами")

    
@dp.message_handler(state=Form.gold)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gold'] = int(message.text)
        await Form.next()
        await message.reply("Введи своё имя из игры:")


    
@dp.message_handler(state=Form.nameGame)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nameGame'] = message.text
        await Form.next()
        await message.reply("Теперь выстави скин на рынок. И напиши его название сюда в точности как в игре")

@dp.message_handler(state=Form.nameSkin)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        money = float(BotDB.get_records(message.chat.id)[3])
        money = money - int(data['gold'])
        BotDB.update_money(message.chat.id, money)
        data['nameSkin'] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
        main = types.KeyboardButton('главное меню')
        markup.add(main)
        await bot.send_message(message.chat.id, "Скоро твой скин купят и голда зачислится тебе на счёт. Главное не убирай скин с рынка.", reply_markup=markup)
        
    await state.finish()

@dp.callback_query_handler(text="one_upgrade")
async def send_random_value(call: types.CallbackQuery):
  result = BotDB.get_records(call.from_user.id)
  moneyR = int(result[4])
  plusmoney = float(result[2])
  if moneyR >= 1:
    moneyR = moneyR - 1
    plusmoney = plusmoney + 0.001
    BotDB.update_moneyR(call.from_user.id, moneyR)
    BotDB.update_plusmoney(call.from_user.id, plusmoney)
    await bot.send_message(call.from_user.id, "улучшено")
  else:
    await bot.send_message(call.from_user.id, "Недостаточно средств на балансе. Пожалуйста пополни баланс.")

@dp.callback_query_handler(text="two_upgrade")
async def send_random_value(call: types.CallbackQuery):
  result = BotDB.get_records(call.from_user.id)
  moneyR = int(result[4])
  money = float(result[3])
  passive = int(result[5])
  if moneyR >= 10:
    moneyR = moneyR - 10
    money = money + 1
    passive = passive + 1
    BotDB.update_moneyR(call.from_user.id, moneyR)
    BotDB.update_money(call.from_user.id, money)
    BotDB.update_passive(call.from_user.id, passive)
    await bot.send_message(call.from_user.id, "улучшено")
  else:
    await bot.send_message(call.from_user.id, "Недостаточно средств на балансе. Пожалуйста пополни баланс.")

@dp.callback_query_handler(text="pay_pay")
async def send_random_value(call: types.CallbackQuery):
  await Form2.money.set()
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
  main = types.KeyboardButton('/cancel')
  markup.add(main)
  await bot.send_message(call.from_user.id, "Введи сумму пополнения:", reply_markup=markup)

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form2.money)
async def process_age_invalid(message: types.Message):
    return await message.reply("напиши цифрами")
      
 
@dp.message_handler(state=Form2.money)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        money = int(message.text)
        comment = random.randint(10, 100000)
        current_date = date.today()
        BotDB.add_payments(message.from_user.id, money, "не оплачено", comment, current_date)
        markup = types.InlineKeyboardMarkup()
        pay = types.InlineKeyboardButton('оплатить', url=f'https://oplata.qiwi.com/create?publicKey=48e7qUxn9T7RyYE1MVZswX1FRSbE6iyCj2gCRwwF3Dnh5XrasNTx3BGPiMsyXQFNKQhvukniQG8RTVhYm3iPrARsaqgiYcZ4SSbDxPkCacN6HsujC1qK8w9LG5DT7GbQLBbat7QoTtEepNQzSrmYTvZTvPhpetwaoTpadojfyFLgzSoz3wNrGPAqeSZAD&amount={money}&successUrl=http://n953699p.beget.tech/oplata_verifed/good.php&comment={comment}')
        markup.add(pay)
        markuptwo = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        verifed = types.KeyboardButton('проверить оплату')
        cansel = types.KeyboardButton('отмена оплаты')
        markuptwo.add(verifed, cansel)
        await bot.send_message(message.from_user.id, f"к оплате: {money}₽", reply_markup=markup)
        await bot.send_message(message.from_user.id, "после оплаты нажми: проверить оплату", reply_markup=markuptwo)
    await state.finish() 

async def f():
  while True:
    await asyncio.sleep(60*60)
    users = BotDB.get_passive()
    for user in users:
      user_id = user[0]
      passive = int(user[1])
      money = float(user[2])
      money = money + passive
      BotDB.update_money(user_id, money)
      await dp.bot.send_message(user_id, f"☑️ вам зачислено +{passive} голды на счёт")
  

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.create_task(f())
  executor.start_polling(dp, skip_updates=True)
  
  

  

  