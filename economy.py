import random
import sqlite3
import time

import disnake
from disnake.ext import commands, tasks
import datetime
from datetime import datetime, timedelta
import pytz
import asyncio


# Создание бота
intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Определяем роли и их цены
roles = {
    "760998034821349443": 20000,
    "760998034821349444": 20000,
    "760998034821349445": 20000,
    "760998034829344808": 20000,
    "1295719041423511575": 50000,
    "1295719101603381269": 50000,
    "1295719187775488050": 50000,
    "1295719141696868392": 50000,
    "760998034829344812": 80000,
    "760998034829344810": 80000,
    "760998034829344816": 80000,
    "760998034829344815": 80000,
    "1295716063845023775": 150000,
    "1295715951685144626": 150000,
    "1295715743240814653": 150000,
    "1295715690568880159": 150000,
    "1294677582939422793": 300000,
}

# Объединяем роли в один список
role_items = list(roles.items())

# Определяем количество ролей на странице
ROLES_PER_PAGE = 4


def add_roles_to_shop():
    with sqlite3.connect('discord.db') as conn:
        c = conn.cursor()
        # Создаем таблицу, если ее нет
        c.execute("CREATE TABLE IF NOT EXISTS shop (role_id TEXT PRIMARY KEY, price INTEGER)")
        for role_id, price in roles.items():
            # Проверяем, существует ли запись для текущей роли
            c.execute("SELECT role_id FROM shop WHERE role_id = ?", (role_id,))
            result = c.fetchone()
            if not result:
                # Если роли нет в базе, добавляем её
                c.execute("INSERT INTO shop (role_id, price) VALUES (?, ?)", (role_id, price))
        conn.commit()


# Вызов функции для добавления ролей в магазин
add_roles_to_shop()


def setup(bot):
    def get_last_daily(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS daily_claims (user_id INTEGER PRIMARY KEY, last_claim INTEGER)")
            c.execute("SELECT last_claim FROM daily_claims WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else None

    # Функция для обновления времени последнего выполнения команды
    def update_last_daily(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            current_time = int(time.time())
            c.execute("INSERT OR REPLACE INTO daily_claims (user_id, last_claim) VALUES (?, ?)",
                      (user_id, current_time))
            conn.commit()

    # Команда для получения монет
    @bot.command()
    async def daily(ctx):
        user_id = ctx.author.id
        last_claim = get_last_daily(user_id)
        current_time = int(time.time())

        # Проверяем, прошло ли 24 часа (86400 секунд)
        if last_claim is None or (current_time - last_claim) >= 86400:
            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET coins = coins + 1000 WHERE user_id = ?", (user_id,))
                conn.commit()

            update_last_daily(user_id)  # Обновляем время последнего получения награды
            await ctx.send(f"Вы получили 1000 {emoji}")  # Добавлено emoji вместо слова "монет"
        else:
            # Вычисляем оставшееся время до следующей возможности получения монет
            time_left = 86400 - (current_time - last_claim)
            hours, remainder = divmod(time_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"Вы уже получали монеты. \nПопробуйте снова через: **{int(hours)}ч {int(minutes)}м {int(seconds)}с.**"
            )

    ALLOWED_ROLES = [1127563173583654932, 1123262582099296318, 1123262857614721104, 760998034850709535,
                     1291461515467296808]

    def get_last_salary(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS salary_claims (user_id INTEGER PRIMARY KEY, last_claim INTEGER)")
            c.execute("SELECT last_claim FROM salary_claims WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else None

    # Функция для обновления времени последнего выполнения команды
    def update_last_salary(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            current_time = int(time.time())
            c.execute("INSERT OR REPLACE INTO salary_claims (user_id, last_claim) VALUES (?, ?)",
                      (user_id, current_time))
            conn.commit()

    # Команда для получения зарплаты
    @bot.command()
    async def salary_1(ctx):
        member = ctx.author
        user_id = member.id

        # Проверка, есть ли у пользователя одна из разрешенных ролей
        if not any(role.id in ALLOWED_ROLES for role in member.roles):
            await ctx.send("У вас нет прав на получение зарплаты.")
            return

        last_claim = get_last_salary(user_id)
        current_time = int(time.time())
        one_week = 7 * 24 * 60 * 60  # 7 дней в секундах

        # Проверяем, прошло ли 7 дней
        if last_claim is None or (current_time - last_claim) >= one_week:
            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET coins = coins + 7000 WHERE user_id = ?", (user_id,))
                conn.commit()

            update_last_salary(user_id)  # Обновляем время последнего получения награды
            await ctx.send(f"Вы получили 7000 {emoji}")  # Добавлено emoji монет
        else:
            # Вычисляем оставшееся время до следующей возможности получения монет
            time_left = one_week - (current_time - last_claim)
            days, remainder = divmod(time_left, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"Вы уже получили зарплату. \nПопробуйте снова через: **{int(days)}д {int(hours)}ч {int(minutes)}м {int(seconds)}с.**"
            )

    def get_last_daily_vip(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS daily_vip_claims (user_id INTEGER PRIMARY KEY, last_claim INTEGER)")
            c.execute("SELECT last_claim FROM daily_vip_claims WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else None

    def update_last_daily_vip(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            current_time = int(time.time())
            c.execute("INSERT OR REPLACE INTO daily_vip_claims (user_id, last_claim) VALUES (?, ?)",
                      (user_id, current_time))
            conn.commit()

    @bot.command()
    async def daily_vip(ctx):
        # Проверка, есть ли у пользователя нужная роль
        role_id = 1296605940388462684
        if role_id not in [role.id for role in ctx.author.roles]:
            await ctx.send("Эта команда доступна только для VIP участников!")
            return

        user_id = ctx.author.id
        last_claim = get_last_daily_vip(user_id)
        current_time = int(time.time())

        # Проверяем, прошло ли 24 часа (86400 секунд)
        if last_claim is None or (current_time - last_claim) >= 86400:
            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET coins = coins + 2000 WHERE user_id = ?", (user_id,))
                conn.commit()

            update_last_daily_vip(user_id)  # Обновляем время последнего получения награды
            await ctx.send(f"Вы получили 2000 {emoji}!")  # Можно заменить на кастомный эмодзи
        else:
            # Вычисляем оставшееся время до следующей возможности получения монет
            time_left = 86400 - (current_time - last_claim)
            hours, remainder = divmod(time_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"Вы уже получали монеты. \nПопробуйте снова через: **{int(hours)}ч {int(minutes)}м {int(seconds)}с.**"
            )

    def get_last_daily_gold(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS daily_gold_claims (user_id INTEGER PRIMARY KEY, last_claim INTEGER)")
            c.execute("SELECT last_claim FROM daily_gold_claims WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else None

    def update_last_daily_gold(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            current_time = int(time.time())
            c.execute("INSERT OR REPLACE INTO daily_gold_claims (user_id, last_claim) VALUES (?, ?)",
                      (user_id, current_time))
            conn.commit()

    @bot.command()
    async def daily_gold(ctx):
        # Проверка, есть ли у пользователя нужная роль
        role_id = 1296606912959217786
        if role_id not in [role.id for role in ctx.author.roles]:
            await ctx.send("Эта команда доступна только для участников с определённой ролью!")
            return

        user_id = ctx.author.id
        last_claim = get_last_daily_gold(user_id)
        current_time = int(time.time())

        # Проверяем, прошло ли 24 часа (86400 секунд)
        if last_claim is None or (current_time - last_claim) >= 86400:
            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET coins = coins + 5000 WHERE user_id = ?", (user_id,))
                conn.commit()

            update_last_daily_gold(user_id)  # Обновляем время последнего получения награды
            await ctx.send(f"Вы получили 5000 {emoji}!")
        else:
            # Вычисляем оставшееся время до следующей возможности получения монет
            time_left = 86400 - (current_time - last_claim)
            hours, remainder = divmod(time_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"Вы уже получали монеты. \nПопробуйте снова через: **{int(hours)}ч {int(minutes)}м {int(seconds)}с.**"
            )

    def get_last_daily_platinum(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS daily_platinum_claims (user_id INTEGER PRIMARY KEY, last_claim INTEGER)")
            c.execute("SELECT last_claim FROM daily_platinum_claims WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else None

    def update_last_daily_platinum(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            current_time = int(time.time())
            c.execute("INSERT OR REPLACE INTO daily_platinum_claims (user_id, last_claim) VALUES (?, ?)",
                      (user_id, current_time))
            conn.commit()

    @bot.command()
    async def daily_platinum(ctx):
        # Проверка, есть ли у пользователя нужная роль
        role_id = 1296606967774838866
        if role_id not in [role.id for role in ctx.author.roles]:
            await ctx.send("Эта команда доступна только для участников с платиновой ролью!")
            return

        user_id = ctx.author.id
        last_claim = get_last_daily_platinum(user_id)
        current_time = int(time.time())

        # Проверяем, прошло ли 24 часа (86400 секунд)
        if last_claim is None or (current_time - last_claim) >= 86400:
            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET coins = coins + 10000 WHERE user_id = ?", (user_id,))
                conn.commit()

            update_last_daily_platinum(user_id)  # Обновляем время последнего получения награды
            await ctx.send(f"Вы получили 10,000 {emoji}]!")
        else:
            # Вычисляем оставшееся время до следующей возможности получения монет
            time_left = 86400 - (current_time - last_claim)
            hours, remainder = divmod(time_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"Вы уже получали монеты. \nПопробуйте снова через: **{int(hours)}ч {int(minutes)}м {int(seconds)}с.**"
            )

    @bot.command(aliases=['bal', 'баланс', 'бал'])
    async def balance(ctx, member: disnake.Member = None):
        # Если участник не указан, показываем баланс отправителя команды
        if member is None:
            member = ctx.author

        user_id = member.id
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = c.fetchone()

        # Проверяем, существует ли пользователь в базе данных
        if result is not None:
            balance = result[0]
            await ctx.send(f"Баланс участника {member.mention}: {balance} {emoji}")
        else:
            await ctx.send(f"{member.mention} не найден в базе данных.")

    def get_balance(user_id):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            balance = c.fetchone()
            return balance[0] if balance else 0  # Возвращает 0, если пользователь не найден

    emoji = "<:fam_coin:1295370513383948339>"

    @bot.command()
    async def shop_2(ctx, page: int = 1):
        # Обновленные цены на роли
        cheap_roles = [(role_id, price) for role_id, price in role_items if price == 20000]
        mid_roles = [(role_id, price) for role_id, price in role_items if price == 50000]
        expensive_roles = [(role_id, price) for role_id, price in role_items if
                           price == 80000]  # Цена изменена на 100k
        very_expensive_roles = [(role_id, price) for role_id, price in role_items if
                                price == 150000]  # Цена изменена на 350k
        ultra_expensive_roles = [(role_id, price) for role_id, price in role_items if
                                 price == 300000]  # Цена изменена на 600k

        # Объединяем все роли для общей нумерации
        all_roles = cheap_roles + mid_roles + expensive_roles + very_expensive_roles + ultra_expensive_roles

        # Определяем количество страниц для каждой категории
        total_cheap_pages = (len(cheap_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_mid_pages = (len(mid_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_expensive_pages = (len(expensive_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_very_expensive_pages = (len(very_expensive_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_ultra_expensive_pages = (len(ultra_expensive_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE

        total_pages = total_cheap_pages + total_mid_pages + total_expensive_pages + total_very_expensive_pages + total_ultra_expensive_pages

        # Определяем какие роли показывать на текущей странице
        if page <= total_cheap_pages:
            items = cheap_roles
            category_start_index = 0
        elif page <= total_cheap_pages + total_mid_pages:
            items = mid_roles
            category_start_index = total_cheap_pages * ROLES_PER_PAGE
            page -= total_cheap_pages
        elif page <= total_cheap_pages + total_mid_pages + total_expensive_pages:
            items = expensive_roles
            category_start_index = (total_cheap_pages + total_mid_pages) * ROLES_PER_PAGE
            page -= (total_cheap_pages + total_mid_pages)
        elif page <= total_cheap_pages + total_mid_pages + total_expensive_pages + total_very_expensive_pages:
            items = very_expensive_roles
            category_start_index = (total_cheap_pages + total_mid_pages + total_expensive_pages) * ROLES_PER_PAGE
            page -= (total_cheap_pages + total_mid_pages + total_expensive_pages)
        else:
            items = ultra_expensive_roles
            category_start_index = (
                                           total_cheap_pages + total_mid_pages + total_expensive_pages + total_very_expensive_pages) * ROLES_PER_PAGE
            page -= (total_cheap_pages + total_mid_pages + total_expensive_pages + total_very_expensive_pages)

        # Проверяем наличие ролей на текущей странице
        start_index = (page - 1) * ROLES_PER_PAGE
        end_index = start_index + ROLES_PER_PAGE
        items = items[start_index:end_index]

        if not items:
            await ctx.send("На этой странице нет доступных ролей.")
            return

        # Создаем embed
        embed = disnake.Embed(title="Магазин ролей", color=0x2F3136)
        embed.set_image(url="https://is.gd/Q1MaOD")
        embed.set_footer(text="Для покупки товара, введите: !buy + номер товара")

        # Добавляем роли в embed с уникальными номерами и эмодзи монетки возле цены
        for index, (role_id, price) in enumerate(items):
            unique_index = category_start_index + start_index + index + 1
            role = ctx.guild.get_role(int(role_id))
            if role:
                embed.add_field(
                    name="\u200b",  # Пустое имя поля, использован невидимый символ
                    value=f"{unique_index}. Роль: {role.mention}\nЦена: {price} {emoji}",
                    inline=False
                )

        # Добавляем кнопки для навигации
        buttons = [
            disnake.ui.Button(label="⬅️ Назад", style=disnake.ButtonStyle.blurple, custom_id="previous_page"),
            disnake.ui.Button(label="➡️ Вперед", style=disnake.ButtonStyle.blurple, custom_id="next_page"),
        ]

        view = disnake.ui.View()
        for button in buttons:
            view.add_item(button)

        # Отправляем сообщение с embed и кнопками
        await ctx.send(embed=embed, view=view)

        # Сохраняем информацию о текущей странице
        view.current_page = page
        view.total_pages = total_pages

        # Callback для кнопок
        async def button_callback(interaction: disnake.MessageInteraction):
            if interaction.user != ctx.author:
                return

            button_id = interaction.data['custom_id']

            if button_id == "next_page" and view.current_page < view.total_pages:
                view.current_page += 1
            elif button_id == "previous_page" and view.current_page > 1:
                view.current_page -= 1

            await interaction.response.edit_message(embed=await get_shop_embed(ctx, view.current_page), view=view)

        for button in buttons:
            button.callback = button_callback

    async def get_shop_embed(ctx, page):
        cheap_roles = [(role_id, price) for role_id, price in role_items if price == 20000]
        mid_roles = [(role_id, price) for role_id, price in role_items if price == 50000]
        expensive_roles = [(role_id, price) for role_id, price in role_items if price == 80000]
        very_expensive_roles = [(role_id, price) for role_id, price in role_items if price == 150000]
        ultra_expensive_roles = [(role_id, price) for role_id, price in role_items if price == 300000]

        items = []
        total_cheap_pages = (len(cheap_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_mid_pages = (len(mid_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_expensive_pages = (len(expensive_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_very_expensive_pages = (len(very_expensive_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE
        total_ultra_expensive_pages = (len(ultra_expensive_roles) + ROLES_PER_PAGE - 1) // ROLES_PER_PAGE

        if page <= total_cheap_pages:
            items = cheap_roles
            category_start_index = 0
        elif page <= total_cheap_pages + total_mid_pages:
            items = mid_roles
            category_start_index = total_cheap_pages * ROLES_PER_PAGE
            page -= total_cheap_pages
        elif page <= total_cheap_pages + total_mid_pages + total_expensive_pages:
            items = expensive_roles
            category_start_index = (total_cheap_pages + total_mid_pages) * ROLES_PER_PAGE
            page -= (total_cheap_pages + total_mid_pages)
        elif page <= total_cheap_pages + total_mid_pages + total_expensive_pages + total_very_expensive_pages:
            items = very_expensive_roles
            category_start_index = (total_cheap_pages + total_mid_pages + total_expensive_pages) * ROLES_PER_PAGE
            page -= (total_cheap_pages + total_mid_pages + total_expensive_pages)
        else:
            items = ultra_expensive_roles
            category_start_index = (
                                           total_cheap_pages + total_mid_pages + total_expensive_pages + total_very_expensive_pages) * ROLES_PER_PAGE
            page -= (total_cheap_pages + total_mid_pages + total_expensive_pages + total_very_expensive_pages)

        start_index = (page - 1) * ROLES_PER_PAGE
        end_index = start_index + ROLES_PER_PAGE
        items = items[start_index:end_index]

        embed = disnake.Embed(title="Магазин ролей", color=0x2F3136)
        embed.set_image(url="https://is.gd/Q1MaOD")
        embed.set_footer(text="Для покупки товара, введите: !buy + номер товара")

        for index, (role_id, price) in enumerate(items):
            unique_index = category_start_index + start_index + index + 1
            role = ctx.guild.get_role(int(role_id))
            if role:
                embed.add_field(
                    name="\u200b",
                    value=f"{unique_index}. Роль: {role.mention}\nЦена: {price} {emoji}",
                    inline=False
                )

        return embed

    ROLE_DURATION = timedelta(days=182)  # 6 месяцев

    @bot.command()
    async def buy_1(ctx, position: int):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT role_id, price FROM shop")
            items = c.fetchall()

        # Проверка корректности номера позиции
        if position < 1 or position > len(items):
            await ctx.send("Некорректный номер позиции. Пожалуйста, введите правильный номер.")
            return

        role_id = items[position - 1][0]
        price = items[position - 1][1]
        user_id = ctx.author.id

        # Проверка, есть ли у пользователя уже эта роль
        role = ctx.guild.get_role(role_id)
        if role in ctx.author.roles:
            await ctx.send(f"У вас уже есть роль **{role.name}**, поэтому нельзя купить повторно.")
            return

        # Проверка баланса пользователя
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            balance = c.fetchone()

        if not balance or balance[0] < price:
            await ctx.send("У вас недостаточно монет для покупки этой роли.")
            return

        # Обновление баланса и добавление роли
        new_balance = balance[0] - price
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
            c.execute("INSERT OR REPLACE INTO user_roles (user_id, role_id, expire_date) VALUES (?, ?, ?)",
                      (user_id, role_id, datetime.now() + ROLE_DURATION))
            conn.commit()

        # Выдача роли участнику
        await ctx.author.add_roles(role)
        await ctx.send(f"Вы купили роль **{role.name}** за {price} {emoji}! Выдана на срок: 6 месяцев.")

    # Фоновая задача для проверки и снятия ролей по истечению срока

    @bot.command()
    async def top_coins(ctx):
        emoji_id = 1295370513383948339  # ID кастомного эмодзи
        emoji = bot.get_emoji(emoji_id)

        if not emoji:
            await ctx.send("Эмодзи не найдено.")
            return

        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT user_id, coins FROM users WHERE presence = 1 ORDER BY coins DESC")
            all_users = c.fetchall()

        if not all_users:
            await ctx.send("Топ пользователей пуст.")
            return

        embed = disnake.Embed(title="Топ 10 пользователей по монетам", color=0x000000)
        index = 0

        for user_id, coins in all_users:
            user = ctx.guild.get_member(user_id)
            if user is None:  # Пропускаем, если пользователь вышел с сервера
                continue

            index += 1
            user_nickname = user.nick if user.nick else user.name
            embed.add_field(
                name="\u200b",
                value=f"{index}. {user.mention} ({user_nickname}) — {coins} {emoji}",
                inline=False
            )

            if index == 10:  # Ограничиваем топ 10
                break

        await ctx.send(embed=embed)

    @bot.command()
    async def top(ctx):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT user_id, level, exp FROM users WHERE presence = 1 ORDER BY level DESC, exp DESC")
            all_users = c.fetchall()

        if not all_users:
            await ctx.send("Топ пользователей пуст.")
            return

        embed = disnake.Embed(title="Топ 10 участников по уровню и опыту", color=0x00FF00)
        index = 0

        for user_id, level, exp in all_users:
            user = ctx.guild.get_member(user_id)
            if user is None:  # Пропускаем, если пользователь вышел с сервера
                continue

            index += 1
            user_nickname = user.nick if user.nick else user.name
            embed.add_field(
                name="\u200b",
                value=f"{index}. {user.mention} ({user_nickname}) — Уровень: {level}, Опыт: {exp}",
                inline=False
            )

            if index == 10:  # Ограничиваем топ 10
                break

        await ctx.send(embed=embed)

    @bot.command()
    async def top_voice(ctx):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute(
                "SELECT user_id, time_spent_in_voice_channels FROM users WHERE presence = 1 ORDER BY time_spent_in_voice_channels DESC"
            )
            all_users = c.fetchall()

        if not all_users:
            await ctx.send("Топ пользователей пуст.")
            return

        embed = disnake.Embed(title="Топ 10 голосовой активности 🎙️", color=0x000000)
        index = 0

        for user_id, time_spent in all_users:
            user = ctx.guild.get_member(user_id)
            if user is None:  # Пропускаем, если пользователь вышел с сервера
                continue

            index += 1
            hours, remainder = divmod(time_spent, 3600)
            minutes, _ = divmod(remainder, 60)
            user_nickname = user.nick if user.nick else user.name
            embed.add_field(
                name="\u200b",
                value=f"{index}. {user.mention} ({user_nickname}) — {int(hours)}ч {int(minutes)}мин",
                inline=False
            )

            if index == 10:  # Ограничиваем топ 10
                break

        await ctx.send(embed=embed)

    @bot.command(name="set_voice_time")
    @commands.has_permissions(administrator=True)
    async def set_voice_time(ctx, member: disnake.Member, time: int, unit: str):
        """
        Команда для изменения времени голосовой активности пользователя.
        """
        # Подключаемся к базе данных
        conn = sqlite3.connect('discord.db')
        cursor = conn.cursor()

        # Проверяем правильность ввода единицы времени
        if unit not in ["minutes", "hours"]:
            await ctx.send("Пожалуйста, укажите единицу времени: 'minutes' или 'hours'.")
            return

        # Конвертируем время в секунды
        seconds_to_add = time * 60 if unit == "minutes" else time * 3600

        # Получаем текущее время пользователя
        cursor.execute("SELECT time_spent_in_voice_channels FROM users WHERE user_id = ?", (member.id,))
        result = cursor.fetchone()

        if result is None:
            # Если записи нет, создаем новую (только если время добавляется)
            if seconds_to_add >= 0:
                cursor.execute(
                    "INSERT INTO users (user_id, time_spent_in_voice_channels) VALUES (?, ?)",
                    (member.id, seconds_to_add)
                )
            else:
                await ctx.send("У пользователя нет времени, и его нельзя уменьшить.")
                conn.close()
                return
        else:
            # Обновляем существующее время
            current_time = result[0] or 0  # Если значение None, считаем, что 0
            new_time = current_time + seconds_to_add

            # Не допускаем отрицательных значений
            if new_time < 0:
                new_time = 0

            cursor.execute(
                "UPDATE users SET time_spent_in_voice_channels = ? WHERE user_id = ?",
                (new_time, member.id)
            )

        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()

        # Форматируем изменения для ответа
        if seconds_to_add > 0:
            await ctx.send(f"У {member.mention} добавлено {seconds_to_add // 3600} часов голосовой активности.")
        elif seconds_to_add < 0:
            await ctx.send(f"У {member.mention} вычтено {abs(seconds_to_add // 3600)} часов голосовой активности.")
        else:
            await ctx.send(f"Время голосовой активности {member.mention} не изменено.")

    @bot.command()
    @commands.has_permissions(
        manage_roles=True)
    async def give_coins(ctx, member: disnake.Member, amount: int):
        if amount <= 0:
            await ctx.send("Количество монет должно быть положительным.")
            return

        # Получаем ID пользователя, которому будут даны монеты
        user_id = member.id

        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            # Обновляем баланс пользователя, добавляя указанное количество монет
            c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
            conn.commit()

        # Получаем новый баланс после добавления монет
        new_balance = get_balance(user_id)
        await ctx.send(f"Участник {member.mention} получил {amount} {emoji}!")

    @bot.command()
    @commands.has_permissions(
        manage_roles=True)  # Позволяем только участникам с правами управления ролями использовать эту команду
    async def take_coins(ctx, member: disnake.Member, amount: int):
        user_id = member.id

        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()

            # Проверяем, достаточно ли у участника монет для вычитания
            c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = c.fetchone()

            if result is None:
                await ctx.send(f"{member.mention} не найден в базе данных.")
                return

            current_balance = result[0]

            if current_balance < amount:
                await ctx.send(f"У {member.mention} недостаточно монет для вычитания.")
                return

            # Вычитаем монеты
            new_balance = current_balance - amount
            c.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
            conn.commit()

        await ctx.send(f"У {member.mention} было вычтено {amount} монет. Новый баланс: {new_balance} монет.")

    # Команда для просмотра доступных кейсов
    # Команда для открытия кейса
    @bot.command()
    async def open_case(ctx, case_name: str):
        user_id = ctx.author.id
        guild = ctx.guild

        # Подключение к базе данных
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()

            # Проверяем наличие кейса
            c.execute("SELECT price FROM cases WHERE case_name = ?", (case_name,))
            case_data = c.fetchone()
            if not case_data:
                await ctx.send("Такого кейса не существует.")
                return

            price = case_data[0]

            # Проверяем баланс пользователя
            c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            user_balance = c.fetchone()[0]

            if user_balance < price:
                await ctx.send(f"У вас недостаточно монет для открытия этого кейса. Цена кейса: {price} {emoji}.")
                return

            # Списываем монеты за открытие кейса
            c.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (price, user_id))
            conn.commit()

            # Получаем роли и шансы выпадения для кейса
            c.execute("SELECT role_id, drop_chance FROM case_roles WHERE case_name = ?", (case_name,))
            roles_data = c.fetchall()

            if not roles_data:
                await ctx.send(f"Кейс **{case_name}** не содержит ролей.")
                return

            # Генерация случайного выпадения роли
            drop_result = random.random()
            cumulative_chance = 0

            for role_id, drop_chance in roles_data:
                cumulative_chance += drop_chance
                if drop_result <= cumulative_chance:
                    role = guild.get_role(role_id)
                    if not role:
                        await ctx.send(f"Роль с ID {role_id} не найдена на сервере.")
                        return

                    # Проверяем, есть ли уже у пользователя эта роль
                    member = ctx.author
                    if role in member.roles:
                        # Если роль уже есть, возвращаем монеты
                        c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (price, user_id))
                        conn.commit()
                        await ctx.send(
                            f"У вас уже есть роль **{role.name}**.\nВам возвращено {price} {emoji} вместо роли."
                        )
                        return

                    # Выдаем роль на 3 месяца или 1 год в зависимости от кейса
                    await member.add_roles(role)

                    # Проверка на исключение для определенного кейса
                    if case_name == "NEWYEAR":  # Замените "special_case" на название вашего кейса
                        expire_date = datetime.now() + timedelta(days=365)  # 1 год
                        await ctx.send(f"Поздравляю, {ctx.author.mention}, вы получили роль **{role.name}** на 1 год!")
                    else:
                        expire_date = datetime.now() + timedelta(days=90)  # 3 месяца
                        await ctx.send(
                            f"Поздравляю, {ctx.author.mention}, вы получили роль **{role.name}** на 3 месяца!")

                    # Сохраняем данные в таблицу user_roles
                    c.execute(
                        "INSERT INTO user_roles (user_id, role_id, expire_date) VALUES (?, ?, ?)",
                        (user_id, role_id, expire_date)
                    )
                    conn.commit()
                    return

            # Если ничего не выпало
            await ctx.send(f"К сожалению, вы не получили ничего из кейса **{case_name}**.")

    # Команда для добавления кейса с ценой
    @bot.command()
    async def create_case(ctx, case_name: str, price: int):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()

            # Добавляем новый кейс в базу данных с названием и ценой
            c.execute("INSERT INTO cases (case_name, price) VALUES (?, ?)", (case_name, price))
            conn.commit()

        await ctx.send(f"Кейс **{case_name}** добавлен с ценой {price} {emoji}.")

    @bot.command()
    async def add_case_role(ctx, case_name: str, role: disnake.Role, drop_chance: float):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()

            # Добавляем роль в кейс с указанным шансом выпадения
            c.execute("INSERT INTO case_roles (case_name, role_id, drop_chance) VALUES (?, ?, ?)",
                      (case_name, role.id, drop_chance))
            conn.commit()

        await ctx.send(f"Роль **{role.name}** добавлена в кейс **{case_name}** с шансом {drop_chance * 100:.2f}%.")


    # Команда для просмотра доступных кейсов с ценами
    @bot.command()
    async def cases(ctx):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT case_name, price FROM cases")
            cases_data = c.fetchall()

        if not cases_data:
            await ctx.send("Нет доступных кейсов.")
            return

        embed = disnake.Embed(title="🎁 Доступные кейсы 🎁", color=0x2F3136)

        for idx, (case_name, price) in enumerate(cases_data, 1):  # Добавляем нумерацию начиная с 1
            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("SELECT role_id, drop_chance FROM case_roles WHERE case_name = ?", (case_name,))
                roles_data = c.fetchall()

            roles_info = "\n".join(
                [f"<@&{role_id}> — {drop_chance * 100:.2f}%" for role_id, drop_chance in roles_data]
            )

            embed.add_field(
                name=f"{idx}. {case_name}",
                value=f"Цена: {price} {emoji}\nРоли:\n{roles_info if roles_info else 'Нет доступных ролей'}",
                inline=False
            )

        await ctx.send(embed=embed)

    # Удаление кейсов
    @bot.command()
    async def remove_case(ctx, case_name: str):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()

            # Удаление кейса из базы данных
            c.execute("DELETE FROM cases WHERE case_name = ?", (case_name,))
            conn.commit()

        await ctx.send(f"Кейс **{case_name}** успешно удален.")

    class ButtonView(disnake.ui.View):
        def __init__(self, message=None, timeout=None):
            super().__init__(timeout=timeout)
            self.message = message

        @disnake.ui.button(label="Нажми, чтобы участвовать!", style=disnake.ButtonStyle.green)
        async def button_callback(self, button: disnake.ui.Button, interaction: disnake.Interaction):
            user_id = interaction.user.id

            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("SELECT user_id FROM giveaway_participants WHERE user_id = ?", (user_id,))
                if c.fetchone():
                    await interaction.response.send_message("Вы уже участвуете!", ephemeral=True)
                    return

                c.execute("INSERT INTO giveaway_participants (user_id) VALUES (?)", (user_id,))
                conn.commit()

            await interaction.response.send_message(f"{interaction.user.mention} добавлен в список участников!",
                                                    ephemeral=True)

            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM giveaway_participants")
                participant_count = c.fetchone()[0]

            if participant_count == 10:
                with sqlite3.connect('discord.db') as conn:
                    c = conn.cursor()
                    c.execute("SELECT user_id FROM giveaway_participants")
                    all_participants = [row[0] for row in c.fetchall()]
                    winner_id = random.choice(all_participants)

                    c.execute("UPDATE users SET coins = coins + 5000 WHERE user_id = ?", (winner_id,))
                    conn.commit()

                    c.execute("DELETE FROM giveaway_participants")
                    c.execute("DELETE FROM giveaway_message")
                    conn.commit()

                winner = interaction.guild.get_member(winner_id)
                await interaction.channel.send(f"🎉 {winner.mention} победил и получает 5,000 монет! 🎉")

                for button in self.children:
                    button.disabled = True
                if self.message:
                    await self.message.edit(view=self)

    async def restore_giveaway(ctx):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT message_id FROM giveaway_message LIMIT 1")
            result = c.fetchone()

        if result:
            message_id = result[0]
            emoji = "<:fam_coin:1295370513383948339>"
            view = ButtonView(timeout=None)  # Не задаем тайм-аут

            try:
                message = await ctx.fetch_message(message_id)
                await message.edit(
                    content=f"**Розыгрыш 5000** {emoji}\n- Необходимо 10 участников :mens:\n- 1 Рандомный победитель :slot_machine:",
                    view=view
                )
                view.message = message
                return view
            except disnake.NotFound:
                with sqlite3.connect('discord.db') as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM giveaway_message")
                    conn.commit()

        return None  # Если сообщения нет, вернуть None

    last_transfer_time = {}
    
    @bot.command()
    async def transfer(ctx, recipient: disnake.Member, amount: int):
        sender = ctx.author

        # Проверка, что команда используется не чаще, чем раз в 15 минут
        cooldown_period = timedelta(minutes=15)
        now = datetime.now()
        last_used = last_transfer_time.get(sender.id)

        if last_used and now - last_used < cooldown_period:
            remaining_time = cooldown_period - (now - last_used)
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await ctx.send(f"Вы можете использовать эту команду снова через {minutes} минут(ы) и {seconds} секунд.")
            return

        # Проверка, что сумма больше 0
        if amount <= 0:
            await ctx.send("Сумма перевода должна быть больше нуля.")
            return

        # Получение баланса отправителя из базы данных
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT coins FROM users WHERE user_id = ?", (sender.id,))
            sender_balance = c.fetchone()

        if sender_balance is None:
            await ctx.send("Ваш аккаунт не найден в базе данных.")
            return

        sender_balance = sender_balance[0]

        # Проверка, что у отправителя достаточно монет
        if sender_balance < amount:
            await ctx.send(f"У вас недостаточно монет. У вас есть {sender_balance}.")
            return

        # Рассчитываем комиссию (30%)
        commission = int(amount * 0.30)
        final_amount = amount - commission

        # Получаем баланс получателя
        c.execute("SELECT coins FROM users WHERE user_id = ?", (recipient.id,))
        recipient_balance = c.fetchone()

        if recipient_balance is None:
            await ctx.send(f"Пользователь {recipient.name} не найден в базе данных.")
            return

        # Перевод монет
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (amount, sender.id))
            c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (final_amount, recipient.id))
            conn.commit()

        # Обновляем время последнего использования команды
        last_transfer_time[sender.id] = now

        # Уведомление в указанном канале
        log_channel_id = 760998035483262977
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(
                f"{recipient.mention} вы получили {final_amount} {emoji} от {sender.mention}")
        else:
            await ctx.send("Не удалось найти указанный канал для уведомлений.")

    @bot.command()
    async def giveaway(ctx):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS giveaway_participants (user_id INTEGER PRIMARY KEY)")
            c.execute("CREATE TABLE IF NOT EXISTS giveaway_message (message_id INTEGER)")
            conn.commit()

        # Восстановить активный розыгрыш, если он уже существует
        view = await restore_giveaway(ctx)

        if view is None:  # Если активного розыгрыша нет, создаем новый
            emoji = "<:fam_coin:1295370513383948339>"
            view = ButtonView(timeout=None)  # Кнопка активна до конца розыгрыша
            message = await ctx.send(
                f"**Розыгрыш 5000** {emoji}\n- Необходимо 10 участников :mens:\n- 1 Рандомный победитель :slot_machine:",
                view=view)
            view.message = message

            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO giveaway_message (message_id) VALUES (?)", (message.id,))
                conn.commit()

    # --- Добавление ролей в магазин ---
    def populate_shop_roles():
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            roles_1 = [
                # Все роли за месяц
                (760998034821349443, 'Роль 1', 'Месяц', 10000),
                (760998034821349444, 'Роль 2', 'Месяц', 10000),
                (760998034821349445, 'Роль 3', 'Месяц', 10000),
                (760998034829344808, 'Роль 4', 'Месяц', 10000),
                (1295719041423511575, 'Роль 5', 'Месяц', 25000),
                (1295719101603381269, 'Роль 6', 'Месяц', 25000),
                (1295719187775488050, 'Роль 7', 'Месяц', 25000),
                (1295719141696868392, 'Роль 8', 'Месяц', 25000),
                (760998034829344812, 'Роль 9', 'Месяц', 40000),
                (760998034829344810, 'Роль 10', 'Месяц', 40000),
                (760998034829344816, 'Роль 11', 'Месяц', 40000),
                (760998034829344815, 'Роль 12', 'Месяц', 40000),
                (1295716063845023775, 'Роль 13', 'Месяц', 75000),
                (1295715951685144626, 'Роль 14', 'Месяц', 75000),
                (1295715743240814653, 'Роль 15', 'Месяц', 75000),
                (1295715690568880159, 'Роль 16', 'Месяц', 75000),
                (1294677582939422793, 'Роль 17', 'Месяц', 150000),

                # Все роли за 3 месяца
                (760998034821349443, 'Роль 1', '3 месяца', 20000),
                (760998034821349444, 'Роль 2', '3 месяца', 20000),
                (760998034821349445, 'Роль 3', '3 месяца', 20000),
                (760998034829344808, 'Роль 4', '3 месяца', 20000),
                (1295719041423511575, 'Роль 5', '3 месяца', 50000),
                (1295719101603381269, 'Роль 6', '3 месяца', 50000),
                (1295719187775488050, 'Роль 7', '3 месяца', 50000),
                (1295719141696868392, 'Роль 8', '3 месяца', 50000),
                (760998034829344812, 'Роль 9', '3 месяца', 80000),
                (760998034829344810, 'Роль 10', '3 месяца', 80000),
                (760998034829344816, 'Роль 11', '3 месяца', 80000),
                (760998034829344815, 'Роль 12', '3 месяца', 80000),
                (1295716063845023775, 'Роль 13', '3 месяца', 150000),
                (1295715951685144626, 'Роль 14', '3 месяца', 150000),
                (1295715743240814653, 'Роль 15', '3 месяца', 150000),
                (1295715690568880159, 'Роль 16', '3 месяца', 150000),
                (1294677582939422793, 'Роль 17', '3 месяца', 300000),

                # Все роли за 6 месяцев
                (760998034821349443, 'Роль 1', '6 месяцев', 30000),
                (760998034821349444, 'Роль 2', '6 месяцев', 30000),
                (760998034821349445, 'Роль 3', '6 месяцев', 30000),
                (760998034829344808, 'Роль 4', '6 месяцев', 30000),
                (1295719041423511575, 'Роль 5', '6 месяцев', 75000),
                (1295719101603381269, 'Роль 6', '6 месяцев', 75000),
                (1295719187775488050, 'Роль 7', '6 месяцев', 75000),
                (1295719141696868392, 'Роль 8', '6 месяцев', 75000),
                (760998034829344812, 'Роль 9', '6 месяцев', 120000),
                (760998034829344810, 'Роль 10', '6 месяцев', 120000),
                (760998034829344816, 'Роль 11', '6 месяцев', 120000),
                (760998034829344815, 'Роль 12', '6 месяцев', 120000),
                (1295716063845023775, 'Роль 13', '6 месяцев', 225000),
                (1295715951685144626, 'Роль 14', '6 месяцев', 225000),
                (1295715743240814653, 'Роль 15', '6 месяцев', 225000),
                (1295715690568880159, 'Роль 16', '6 месяцев', 225000),
                (1294677582939422793, 'Роль 17', '6 месяцев', 450000),

                # Все роли за год
                (760998034821349443, 'Роль 1', 'Год', 50000),
                (760998034821349444, 'Роль 2', 'Год', 50000),
                (760998034821349445, 'Роль 3', 'Год', 50000),
                (760998034829344808, 'Роль 4', 'Год', 50000),
                (1295719041423511575, 'Роль 5', 'Год', 125000),
                (1295719101603381269, 'Роль 6', 'Год', 125000),
                (1295719187775488050, 'Роль 7', 'Год', 125000),
                (1295719141696868392, 'Роль 8', 'Год', 125000),
                (760998034829344812, 'Роль 9', 'Год', 200000),
                (760998034829344810, 'Роль 10', 'Год', 200000),
                (760998034829344816, 'Роль 11', 'Год', 200000),
                (760998034829344815, 'Роль 12', 'Год', 200000),
                (1295716063845023775, 'Роль 13', 'Год', 375000),
                (1295715951685144626, 'Роль 14', 'Год', 375000),
                (1295715743240814653, 'Роль 15', 'Год', 375000),
                (1295715690568880159, 'Роль 16', 'Год', 375000),
                (1294677582939422793, 'Роль 17', 'Год', 750000),

                # Все роли навсегда
                (760998034821349443, 'Роль 1', 'Навсегда', 100000),
                (760998034821349444, 'Роль 2', 'Навсегда', 100000),
                (760998034821349445, 'Роль 3', 'Навсегда', 100000),
                (760998034829344808, 'Роль 4', 'Навсегда', 100000),
                (1295719041423511575, 'Роль 5', 'Навсегда', 250000),
                (1295719101603381269, 'Роль 6', 'Навсегда', 250000),
                (1295719187775488050, 'Роль 7', 'Навсегда', 250000),
                (1295719141696868392, 'Роль 8', 'Навсегда', 250000),
                (760998034829344812, 'Роль 9', 'Навсегда', 400000),
                (760998034829344810, 'Роль 10', 'Навсегда', 400000),
                (760998034829344816, 'Роль 11', 'Навсегда', 400000),
                (760998034829344815, 'Роль 12', 'Навсегда', 400000),
                (1295716063845023775, 'Роль 13', 'Навсегда', 750000),
                (1295715951685144626, 'Роль 14', 'Навсегда', 750000),
                (1295715743240814653, 'Роль 15', 'Навсегда', 750000),
                (1295715690568880159, 'Роль 16', 'Навсегда', 750000),
                (1294677582939422793, 'Роль 17', 'Навсегда', 1500000),
            ]


            for role_id, role_name, duration, price in roles_1:
                # Проверяем, существует ли такая роль с конкретной длительностью
                c.execute(
                    "SELECT 1 FROM shop_roles WHERE role_id = ? AND duration = ?",
                    (role_id, duration)
                )
                if not c.fetchone():  # Если запись не найдена, добавляем её
                    c.execute(
                        """INSERT INTO shop_roles (role_id, role_name, duration, price) VALUES (?, ?, ?, ?)""",
                        (role_id, role_name, duration, price)
                    )

            conn.commit()

    populate_shop_roles()

    @bot.command()
    async def give_voice_coins(ctx, coins: int):
        # Проверяем, имеет ли автор команду роль с ID 1135313711695921222
        required_role_id = 1135313711695921222
        if not any(role.id == required_role_id for role in ctx.author.roles):
            await ctx.send("У вас нет прав использовать эту команду.")
            return

        # Проверяем, находится ли автор в голосовом канале
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Вы должны находиться в голосовом канале, чтобы использовать эту команду.")
            return

        # Получаем голосовой канал, в котором находится автор
        voice_channel = ctx.author.voice.channel

        # Участники голосового канала
        members = voice_channel.members

        # Проверяем, что есть участники в канале
        if not members:
            await ctx.send("В голосовом канале никого нет.")
            return

        # Обновление монет для каждого участника
        with sqlite3.connect('discord.db') as conn:
            cursor = conn.cursor()
            for member in members:
                cursor.execute("SELECT coins FROM users WHERE user_id = ?", (member.id,))
                user_data = cursor.fetchone()

                if not user_data:
                    # Если пользователь отсутствует в БД, добавляем запись
                    cursor.execute("INSERT INTO users (user_id, coins) VALUES (?, ?)", (member.id, coins))
                else:
                    # Если пользователь уже есть, обновляем монеты
                    cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (coins, member.id))

            conn.commit()

        # Формируем список упоминаний участников для сообщения
        mentions = ", ".join(member.mention for member in members)

        await ctx.send(f"Всем участникам в голосовом канале начислено {coins} монет! 🎉\n{mentions}")

    @bot.event
    async def on_message(message):
        # ID чата, где функция срабатывает
        allowed_channel_id = 1318603952438247509
        # ID роли, которая должна быть у пользователя
        required_role_id = 1123262857614721104
        # ID упоминаемой роли
        target_role_id = 1291935144827031647
        # ID канала для уведомлений
        notification_channel_id = 900316761520500756
        # Количество монет для начисления
        coins_to_add = 3000

        # Игнорируем сообщения от ботов
        if message.author.bot:
            return

        # Проверка, что сообщение отправлено в нужный канал
        if message.channel.id != allowed_channel_id:
            await bot.process_commands(message)  # Обрабатываем остальные команды
            return

        # Проверка, что пользователь имеет требуемую роль
        if required_role_id not in [role.id for role in message.author.roles]:
            await bot.process_commands(message)
            return

        # Проверка, что упомянута необходимая роль
        mentioned_roles = [role.id for role in message.role_mentions]
        if target_role_id not in mentioned_roles:
            await bot.process_commands(message)
            return

        # Начисление монет
        user_id = message.author.id
        try:
            with sqlite3.connect('discord.db') as conn:
                c = conn.cursor()
                # Убедитесь, что пользователь есть в базе данных, иначе добавляем
                c.execute("INSERT OR IGNORE INTO users (user_id, coins) VALUES (?, ?)", (user_id, 0))
                # Добавляем монеты пользователю
                c.execute("UPDATE users SET coins = COALESCE(coins, 0) + ? WHERE user_id = ?", (coins_to_add, user_id))
                conn.commit()

            # Получение объекта канала для уведомлений
            notification_channel = bot.get_channel(notification_channel_id)
            if notification_channel is not None:
                await notification_channel.send(f"{message.author.mention}, вам начислено {coins_to_add} {emoji} за проведение ивента!")
            else:
                print(f"Не удалось найти канал с ID {notification_channel_id}.")
        except Exception as e:
            print(f"Ошибка при начислении монет: {e}")

        # Обрабатываем остальные команды
        await bot.process_commands(message)

    # --- Команда покупки роли ---
    @bot.command()
    async def buy(ctx, position: int):
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id, role_id, role_name, duration, price FROM shop_roles")
            items = c.fetchall()

        # Проверка корректности номера позиции
        if position < 1 or position > len(items):
            await ctx.send("Некорректный номер позиции. Пожалуйста, введите правильный номер.")
            return

        item = items[position - 1]
        role_id, role_name, duration, price = item[1], item[2], item[3], item[4]
        user_id = ctx.author.id

        # Проверка, есть ли у пользователя уже эта роль
        role = ctx.guild.get_role(role_id)
        if not role:
            await ctx.send("Роль не найдена на сервере.")
            return

        if role in ctx.author.roles:
            await ctx.send(f"У вас уже есть роль **{role.name}**, поэтому нельзя купить повторно.")
            return

        # Проверка баланса пользователя
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            balance = c.fetchone()

        if not balance or balance[0] < price:
            await ctx.send("У вас недостаточно монет для покупки этой роли.")
            return

        # Вычисление срока действия
        if duration == 'Навсегда':
            expire_date = None
        else:
            time_deltas = {
                'Месяц': timedelta(days=30),
                '3 месяца': timedelta(days=90),
                '6 месяцев': timedelta(days=180),
                'Год': timedelta(days=365)
            }
            expire_date = datetime.now() + time_deltas[duration]

        # Обновление баланса и добавление роли
        new_balance = balance[0] - price
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
            if expire_date:
                c.execute("INSERT OR REPLACE INTO user_roles (user_id, role_id, expire_date) VALUES (?, ?, ?)",
                          (user_id, role_id, expire_date))
            else:
                c.execute("INSERT OR REPLACE INTO user_roles (user_id, role_id, expire_date) VALUES (?, ?, NULL)",
                          (user_id, role_id))
            conn.commit()

        # Выдача роли участнику
        await ctx.author.add_roles(role)
        await ctx.send(
            f"Вы купили роль **{role.name}**\n"
            f"Стоимость: {price} {emoji}\n"
            f"Срок действия: {duration}."
        )

    @bot.command()
    async def check_roles(ctx, member: disnake.Member = None):
        """
        Команда для проверки оставшегося времени действия ролей.
        Если указать пользователя, можно посмотреть его роли.
        """
        # Если пользователь не указан, проверяем роли автора команды
        if member is None:
            member = ctx.author

        user_id = member.id
        kiev_tz = pytz.timezone('Europe/Kiev')  # Часовой пояс Киева
        current_time = datetime.now(kiev_tz)  # Текущее время в Киеве

        # Подключаемся к базе данных и получаем роли
        with sqlite3.connect('discord.db') as conn:
            c = conn.cursor()
            c.execute("SELECT role_id, expire_date FROM user_roles WHERE user_id = ?", (user_id,))
            roles = c.fetchall()

        if not roles:
            await ctx.send(f"У {member.mention} нет активных ролей с ограниченным сроком действия.")
            return

        valid_roles = []  # Список для отображения актуальных ролей
        for role_id, expire_date in roles:
            role = ctx.guild.get_role(role_id)

            # Удаляем запись из базы, если роли нет на сервере или у пользователя
            if not role or role not in member.roles:
                with sqlite3.connect('discord.db') as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
                    conn.commit()
                continue

            # Проверяем срок действия роли
            if expire_date:
                expire_datetime = datetime.fromisoformat(expire_date).astimezone(kiev_tz)
                remaining_time = expire_datetime - current_time

                if remaining_time.total_seconds() > 0:
                    days, seconds = divmod(remaining_time.total_seconds(), 86400)
                    hours, seconds = divmod(seconds, 3600)
                    minutes, _ = divmod(seconds, 60)
                    valid_roles.append(
                        f"**{role.name}** — Осталось {int(days)} дней, {int(hours)} часов, {int(minutes)} минут."
                    )
                else:
                    # Если срок истёк, удаляем запись из базы данных
                    with sqlite3.connect('discord.db') as conn:
                        c = conn.cursor()
                        c.execute("DELETE FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
                        conn.commit()
            else:
                valid_roles.append(f"**{role.name}** — Роль действует навсегда.")

        # Добавляем задержку перед выводом результата
        await ctx.send("Подождите, пожалуйста...")
        await asyncio.sleep(2)

        # Выводим результат
        if valid_roles:
            await ctx.send(f"Роли {member.mention}:\n" + "\n".join(valid_roles))
        else:
            await ctx.send(f"У {member.mention} нет актуальных ролей с ограниченным сроком действия.")


