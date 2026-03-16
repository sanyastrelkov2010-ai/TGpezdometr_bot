import asyncio
import random
import json
import logging
import time
from pathlib import Path
from datetime import datetime

from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

TOKEN = "8711888362:AAF-2dY64-1PPmwHUTu205hy5EiAVLdBb6o"

USERS_FILE = Path("users.json")
STATS_FILE = Path("stats.json")

COOLDOWN = 0

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

users = {}
stats = {}

cooldowns = {}
selection_state = {}

# =====================
# ФРАЗЫ СКАНЕРА
# =====================

subjects = [
"Жопный радар","Попометр","Очковый сканер","Ягодичный анализатор",
"Попная нейросеть","Какашечный интеллект","Жопная станция",
"Очковая матрица","Попный детектор","Ягодичный спутник",
"Анальный процессор","Жопный алгоритм","Очковый сенсор"
]

actions = [
"анализирует","сканирует","вычисляет","исследует",
"инициализирует","запускает","моделирует","проверяет"
]

targets = [
"жопную энергию","очковую аномалию","ягодичный поток",
"жопный вихрь","попную сингулярность","очковую галактику",
"анальный портал","жопный резонанс"
]

extras = [
"космического уровня","глобального масштаба",
"критической мощности","эпического масштаба",
"ультра режима","тотального анализа"
]

verbs2 = [
"обнаружена","зафиксирована","найдена","вычислена","идентифицирована"
]

objects2 = [
"аномалия","сигнатура","энергия","матрица","сингулярность"
]

def generate_phrase():

    style=random.randint(1,3)

    if style==1:
        return f"{random.choice(subjects)} {random.choice(actions)} {random.choice(targets)} {random.choice(extras)}..."

    elif style==2:
        return f"{random.choice(verbs2).capitalize()} {random.choice(objects2)} {random.choice(targets)} {random.choice(extras)}..."

    else:
        return f"{random.choice(subjects)} активирует режим {random.choice(targets)} {random.choice(extras)}..."

# =====================
# АВТООТВЕТЫ
# =====================


auto_replies = {

# БАЗОВЫЕ МАТЫ
"хуй": ["⚠ Хуй detected","Сканер обнаружил хуй","Хуевой сигнал","Хуйная аномалия","Хуй detected повторно","🚨 Хуй энергия","Хуйный уровень","Система фиксирует хуй","Хуй сигнал принят","Хуй режим"],
"пизда": ["🚨 Пизда detected","Система сообщает: пизда","Пизда сигнал","Пизда энергия","⚠ Пизда уровень","Пизда активирована","Пизда detected повторно","Сканер пизды","Пизда анализ","Пизда режим"],
"пиздец": ["Это пиздец","⚠ Пиздец detected","Система подтверждает пиздец","🚨 Критический пиздец","Пиздец энергия","Пиздец режим","Пиздец сигнал","Пиздец detected повторно","Пиздец анализ","Пиздец уровень"],
"блять": ["Спокойно без блять","⚠ Блять detected","Блять сигнал","Блять режим","Блять энергия","Блять detected повторно","🚨 Блять активирован","Блять уровень","Сканер блять","Блять анализ"],
"сука": ["⚠ Сукоэнергия","Сучий сигнал","Сука detected","Сука уровень","Сканер суки","🚨 Сучий режим","Сучья энергия","Сука detected повторно","Сука сигнал","Сука анализ"],
"ебать": ["⚠ Ебать detected","Ебать сигнал","Ебать режим","Ебать энергия","Ебать уровень","Ебать detected повторно","🚨 Ебать активирован","Сканер ебать","Ебать анализ","Ебать detected системой"],

# ОСКОРБЛЕНИЯ
"мудак": ["Мудак detected","Мудацкий сигнал","⚠ Мудак уровень","Мудак энергия","Мудак detected повторно","🚨 Мудак режим","Мудак анализ","Сканер мудаков","Мудак сигнал","Мудак активирован"],
"дебил": ["Дебил detected","Дебильный сигнал","⚠ Уровень дебила","Дебил энергия","Дебил detected повторно","🚨 Дебил режим","Дебил анализ","Сканер дебилов","Дебил сигнал","Дебил активирован"],
"идиот": ["Идиот detected","Идиотизм зафиксирован","⚠ Идиот сигнал","Идиот энергия","Идиот detected повторно","🚨 Идиот режим","Идиот анализ","Сканер идиотов","Идиот сигнал","Идиот активирован"],
"лох": ["Лох detected","Лошиная энергия","⚠ Лох сигнал","Лох detected повторно","🚨 Лох режим","Лох анализ","Сканер лохов","Лох сигнал","Лох уровень","Лошиный режим"],
"тупой": ["⚠ Тупость detected","Тупой сигнал","Тупость энергия","Тупой уровень","Тупость detected повторно","🚨 Тупой режим","Тупость анализ","Сканер тупости","Тупой сигнал","Тупость активирована"],

# МЕМЫ
"кринж": ["⚠ Кринж detected","Кринжометр зашкаливает","Кринж энергия","Кринж режим","Кринж detected повторно","🚨 Кринж сигнал","Кринж анализ","Кринж уровень","Сканер кринжа","Кринж активирован"],
"мем": ["Мем detected","📸 Мем энергия","Мем сигнал","Мем режим","Мем detected повторно","📸 Мем активирован","Мем уровень","Мем анализ","Сканер мемов","Мемометр зашкаливает"],
"гигачад": ["🗿 Гигачад detected","Чад энергия","Чад режим","Сигма уровень","🗿 Абсолютный чад","Чад сигнал","Чад detected повторно","🚨 Гигачад активирован","Чад анализ","Сканер чада"],
"сигма": ["🗿 Сигма энергия","Сигма detected","Сигма режим","Сигма сигнал","Сигма уровень","Сигма detected повторно","🚨 Сигма активирован","Сигма анализ","Сканер сигмы","Сигма активирован"],
"лол": ["😂","Лол detected","Лол сигнал","Лол режим","😂 Смешно","Лол detected повторно","😂 Лол","Лол анализ","Лол уровень","Лолометр зашкаливает"],

# ИНТЕРНЕТ СЛЕНГ
"рофл": ["😂 Рофл detected","Рофл энергия","Рофл сигнал","Рофл режим","Рофл detected повторно","🚨 Рофл активирован","Рофл анализ","Сканер рофла","Рофл уровень","Рофл режим"],
"ор": ["ОР detected","ОР энергия","ОР сигнал","ОР режим","ОР detected повторно","🚨 ОР активирован","ОР анализ","Сканер ОРа","ОР уровень","ОР режим"],
"жиза": ["Жиза detected","Жиза энергия","Жиза сигнал","Жиза режим","Жиза detected повторно","🚨 Жиза активирована","Жиза анализ","Сканер жизы","Жиза уровень","Жиза режим"],
"имба": ["Имба detected","Имба энергия","Имба сигнал","Имба режим","Имба detected повторно","🚨 Имба активирована","Имба анализ","Сканер имбы","Имба уровень","Имба режим"],

# ЖИВОТНЫЕ МЕМЫ
"кот": ["🐱 Кот detected","Мяу сигнал","Кошачья энергия","🐱 Кот режим","Кот detected повторно","🐱 Мяу","Сканер котов","Кот уровень","Кот анализ","Кот активирован"],
"собака": ["🐶 Собака detected","Гав сигнал","Собачья энергия","🐶 Пёс режим","Гав detected","🐶 Пёсик","Сканер собак","Собака уровень","Собака анализ","Собака активирована"],

# ОБЫЧНЫЕ СЛОВА
"бот": ["🤖 Я тут","Бот на связи","Система активна","🤖 Онлайн","Бот detected","Бот отвечает","Я слушаю","Бот готов","Система отвечает","Бот анализирует"],
"привет": ["Привет 👋","Йо","Здравствуйте","👋 Хай","Салют","Приветствую","Добрый день","👋 Привет detected","Система приветствует","Рад тебя видеть"],
"спать": ["😴 detected","Сонный режим","Система хочет спать","😴 Сон сигнал","Сон энергия","Сон detected повторно","🚨 Сон режим","Сканер сна","Сон уровень","Сон анализ"],
"пиво": ["🍺 detected","Пивной режим","Пиво энергия","🍺 Пиво сигнал","Пиво detected повторно","🚨 Пиво активировано","Пиво анализ","Сканер пива","Пиво уровень","Пиво режим"],
"водка": ["🥃 detected","Водочный режим","Водка энергия","🥃 Водка сигнал","Водка detected повторно","🚨 Водка активирована","Водка анализ","Сканер водки","Водка уровень","Водка режим"]

}

# =====================
# JSON
# =====================

def load_json(path,default):

    if path.exists():
        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            pass

    return default

def save_json(path,data):

    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

# =====================
# МЕСЯЦ
# =====================

def current_month():
    return datetime.now().strftime("%Y-%m")

# =====================
# ЗАГРУЗКА
# =====================

def load_data():

    global users,stats

    users=load_json(USERS_FILE,{})
    stats=load_json(STATS_FILE,{})

# =====================
# ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
# =====================

async def track_user(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user=update.message.from_user
    uid=str(user.id)

    if uid not in users:

        users[uid]={
            "name":user.first_name,
            "username":user.username
        }

        save_json(USERS_FILE,users)

    else:

        users[uid]["name"]=user.first_name
        users[uid]["username"]=user.username

        save_json(USERS_FILE,users)

# =====================
# АВТООТВЕТ
# =====================

async def auto_reply(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text=update.message.text.lower()

    for word,responses in auto_replies.items():

        if word in text:

            await update.message.reply_text(
                random.choice(responses)
            )
            break

# =====================
# АНИМАЦИЯ СКАНЕРА
# =====================

async def scanning_animation(message):

    msg=await message.reply_text("🔍 Запускаю сканирование...")

    steps=random.randint(3,6)

    for _ in range(steps):

        await asyncio.sleep(random.uniform(1,1.5))

        phrase=generate_phrase()

        try:
            await msg.edit_text(f"🔍 {phrase}")
        except:
            pass

    return msg

# =====================
# /PIDORAS
# =====================

async def pidoras(update:Update,context:ContextTypes.DEFAULT_TYPE):

    chat_id=update.effective_chat.id
    now=time.time()

    state=selection_state.get(chat_id,{"step":0})

    if state["step"]==2:

        last=cooldowns.get(chat_id,0)

        if now-last<COOLDOWN:

            wait=int(COOLDOWN-(now-last))

            await update.message.reply_text(
                f"⏳ Пидоры уже выбраны. Ждите {wait} сек."
            )
            return

        state={"step":0}

    if len(users)<2:

        await update.message.reply_text("Нужно минимум 2 пользователя")
        return

    msg=await scanning_animation(update.message)

    chosen=random.choice(list(users.keys()))
    name=users[chosen]["name"]

    month=current_month()

    if chosen not in stats:
        stats[chosen]={
            "total":0,
            "monthly":{}
        }

    stats[chosen]["total"]+=1
    stats[chosen]["monthly"][month]=stats[chosen]["monthly"].get(month,0)+1

    save_json(STATS_FILE,stats)

    state["step"]+=1
    selection_state[chat_id]=state

    await asyncio.sleep(1)

    await msg.edit_text(f"🏆 Пидор №{state['step']} дня: {name}")

    if state["step"]==2:
        cooldowns[chat_id]=now

# =====================
# /TOP
# =====================

async def top(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if not stats:

        await update.message.reply_text("Статистика пустая")
        return

    month=current_month()

    monthly=[]
    total=[]

    for uid,data in stats.items():

        total.append((uid,data.get("total",0)))

        month_score=data.get("monthly",{}).get(month,0)

        monthly.append((uid,month_score))

    monthly=sorted(monthly,key=lambda x:x[1],reverse=True)[:10]
    total=sorted(total,key=lambda x:x[1],reverse=True)[:10]

    text="🏆 ТОП ПИДОРОВ\n\n"

    text+="🔥 За месяц\n"

    for i,(uid,count) in enumerate(monthly,1):

        name=users.get(uid,{}).get("name","???")

        text+=f"{i}. {name} — {count}\n"

    text+="\n💀 За всё время\n"

    for i,(uid,count) in enumerate(total,1):

        name=users.get(uid,{}).get("name","???")

        text+=f"{i}. {name} — {count}\n"

    await update.message.reply_text(text)
# =====================
# /DICE
# =====================

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):

    value = random.randint(1,6)

    await update.message.reply_text(
        f"🎲 Кубик брошен!\n\nВыпало: {value}"
    )


# =====================
# /COIN
# =====================

async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = random.choice(["🪙 Орёл","🪙 Решка"])

    await update.message.reply_text(
        f"🪙 Монетка подброшена!\n\n{result}"
    )

# =====================
# КОМАНДЫ TELEGRAM
# =====================

async def setup_commands(app):

    commands=[
        BotCommand("pidoras","Выбрать пидора дня"),
        BotCommand("top","Топ пидоров"),
        BotCommand("dice","Бросить кубик"),
        BotCommand("coin","Подбросить монетку")
]

    await app.bot.set_my_commands(commands)

# =====================
# MAIN
# =====================

def main():

    load_data()

    app=ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("pidoras",pidoras))
    app.add_handler(CommandHandler("top",top))
    app.add_handler(CommandHandler("dice",dice))
    app.add_handler(CommandHandler("coin",coin))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND,auto_reply)
    )

    app.add_handler(
        MessageHandler(filters.ALL,track_user)
    )

    app.post_init=setup_commands

    logger.info("Бот запущен")

    app.run_polling()

if __name__=="__main__":
    main()