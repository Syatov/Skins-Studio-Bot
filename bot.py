import disnake
from disnake import ui, Embed, ButtonStyle, ModalInteraction, PermissionOverwrite
from disnake.ext import commands
import asyncio
import logging
import aiohttp
import os
# Инициализация бота
intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
logging.basicConfig(level=logging.INFO)
# Токен вашего бота
TOKEN = ''

# Идентификаторы каналов и ролей
TARGET_CHANNEL_ID = 
PORTFOLIO_CHANNEL_ID = 
REVIEWS_CHANNEL_ID = 
RULES_CHANNEL_ID = 
GOODS_CHANNEL_ID = 
ROLE_ID = 
COMPLETED_ORDER_ROLE_ID = 
# URL-адреса изображений
ORDER_IMAGE_URL = ""
ORDER_SELECT_IMAGE_URL = ""
ORDER_DESCRIPTION_IMAGE_URL = ""
SKIN_ORDER_IMAGE_URL = ""
REVIEVS_IMAGE = ""

# Цены на услуги
PRICES = {
    "Перспектива": 310,
    "Зверинец": 270,
    "Восход": 220,
    "Рендер": 150
}

class ButtonView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    @ui.button(label="Заказать", style=disnake.ButtonStyle.primary, custom_id="order")
    async def order_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        guild = interaction.guild
        role = guild.get_role(ROLE_ID)
        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            role: disnake.PermissionOverwrite(read_messages=True),
            interaction.user: disnake.PermissionOverwrite(read_messages=True)
        }
        new_channel = await guild.create_text_channel(f"заказ-{interaction.user.name}", overwrites=overwrites, category=bot.get_channel(1242883691198546050))
        embed = disnake.Embed(description=f"{interaction.user.mention}, какой товар вы хотите купить?")
        embed.set_image(url=ORDER_SELECT_IMAGE_URL)
        await new_channel.send(embed=embed, view=OrderView())
        await interaction.response.send_message(f"Создан канал для заказа: {new_channel.mention}", ephemeral=True)

    @ui.button(label="Товары", style=disnake.ButtonStyle.secondary, custom_id="goods")
    async def goods_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(f"Перейдите в канал: <#{GOODS_CHANNEL_ID}>", ephemeral=True)

    @ui.button(label="Портфолио", style=disnake.ButtonStyle.secondary, custom_id="portfolio")
    async def portfolio_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(f"Перейдите в канал: <#{PORTFOLIO_CHANNEL_ID}>", ephemeral=True)

    @ui.button(label="Отзывы", style=disnake.ButtonStyle.secondary, custom_id="reviews")
    async def reviews_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(f"Перейдите в канал: <#{REVIEWS_CHANNEL_ID}>", ephemeral=True)

    @ui.button(label="Правила", style=disnake.ButtonStyle.secondary, custom_id="rules")
    async def rules_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(f"Перейдите в канал: <#{RULES_CHANNEL_ID}>", ephemeral=True)

class OrderView(ui.View):
    @ui.button(label="Скин", style=disnake.ButtonStyle.primary, custom_id="skin")
    async def skin_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        embed = disnake.Embed(description="Выберите команду, которая будет делать ваш заказ:")
        embed.set_image(url=ORDER_DESCRIPTION_IMAGE_URL)
        await interaction.channel.send(embed=embed, view=SkinTeamView())

    @ui.button(label="Рендер", style=disnake.ButtonStyle.primary, custom_id="render")
    async def render_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        embed = disnake.Embed(title="Рендер", description="Описание рендера с картинкой")
        embed.set_image(url=SKIN_ORDER_IMAGE_URL)
        await interaction.channel.send(embed=embed, view=RenderView())

    @ui.button(label="Ничего", style=disnake.ButtonStyle.danger, custom_id="cancel")
    async def cancel_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        await interaction.channel.delete()

class SkinTeamView(ui.View):
    @ui.button(label="Перспектива", style=disnake.ButtonStyle.secondary, custom_id="perspective")
    async def perspective_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await self.handle_team_selection(interaction, "Перспектива")

    @ui.button(label="Зверинец", style=disnake.ButtonStyle.secondary, custom_id="zverinec")
    async def zverinec_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await self.handle_team_selection(interaction, "Зверинец")

    @ui.button(label="Восход", style=disnake.ButtonStyle.secondary, custom_id="voshod")
    async def voshod_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await self.handle_team_selection(interaction, "Восход")

    @ui.button(label="Назад", style=disnake.ButtonStyle.danger, custom_id="back")
    async def back_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        embed = disnake.Embed(description="Какой товар вы хотите купить?")
        embed.set_image(url=ORDER_SELECT_IMAGE_URL)
        await interaction.channel.send(embed=embed, view=OrderView())

    async def handle_team_selection(self, interaction, team_name):
        await interaction.message.delete()
        embed = disnake.Embed(description="Опишите ваш заказ:")
        embed.set_image(url=SKIN_ORDER_IMAGE_URL)
        await interaction.channel.send(embed=embed, view=SkinOrderView(team_name))

class SkinOrderView(ui.View):
    def __init__(self, team_name):
        super().__init__(timeout=None)
        self.team_name = team_name

    @ui.button(label="Описать заказ", style=ButtonStyle.primary, custom_id="complete_skin_order")
    async def complete_skin_order_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        modal = SkinOrderModal(self.team_name)
        await interaction.response.send_modal(modal)

    @ui.button(label="Назад", style=ButtonStyle.danger, custom_id="back_to_team_selection")
    async def back_to_team_selection_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        embed = disnake.Embed(description="Выберите команду, которая будет делать ваш заказ:")
        embed.set_image(url=ORDER_DESCRIPTION_IMAGE_URL)
        await interaction.channel.send(embed=embed, view=SkinTeamView())

class SkinOrderModal(ui.Modal):
    def __init__(self, team_name):
        self.team_name = team_name
        components = [
            ui.TextInput(
                label="Описание заказа",
                placeholder="Опишите ваш заказ здесь...",
                style=disnake.TextInputStyle.paragraph,
                custom_id="order_description"
            )
        ]
        super().__init__(title=f"Заказ для команды {self.team_name}", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        description = interaction.text_values['order_description']
        user = interaction.user
        price = PRICES[self.team_name]
        embed = disnake.Embed(description=f"Пользователь: {user.mention}\nЗаказ: Скин\nКоманда: {self.team_name}\nЦена: {price} рублей\nОписание: {description}")
        await interaction.channel.send(embed=embed)
        await interaction.channel.send("Пожалуйста, пришлите в чат референсы изображения.")
        await interaction.response.send_message("Ваш заказ принят и будет обработан.", ephemeral=True)

class RenderView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Описать заказ", style=ButtonStyle.primary, custom_id="complete_render_order")
    async def complete_render_order_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        modal = RenderOrderModal()
        await interaction.response.send_modal(modal)

    @ui.button(label="Назад", style=ButtonStyle.danger, custom_id="back_to_order_selection")
    async def back_to_order_selection_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        embed = disnake.Embed(description="Какой товар вы хотите купить?")
        embed.set_image(url=ORDER_SELECT_IMAGE_URL)
        await interaction.channel.send(embed=embed, view=OrderView())

class RenderOrderModal(ui.Modal):
    def __init__(self):
        components = [
            ui.TextInput(
                label="Описание заказа",
                placeholder="Опишите ваш заказ здесь...",
                style=disnake.TextInputStyle.paragraph,
                custom_id="render_order_description"
            )
        ]
        super().__init__(title="Оформление рендера", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        description = interaction.text_values['render_order_description']
        user = interaction.user
        price = PRICES["Рендер"]
        embed = disnake.Embed(description=f"Пользователь: {user.mention}\nЗаказ: Рендер\nЦена: {price} рублей\nОписание: {description}")
        await interaction.channel.send(embed=embed)
        await interaction.channel.send("Пожалуйста, пришлите в чат референсы изображения.")
        await interaction.response.send_message("Ваш заказ принят и будет обработан.", ephemeral=True)

@bot.event
async def on_ready():
    async def send_initial_message():
        await bot.wait_until_ready()
        while not bot.is_closed():
            channel = bot.get_channel(TARGET_CHANNEL_ID)
            if channel:
                await channel.purge(limit=None)
                embed = disnake.Embed(description="Пожалуйста, выберите один из вариантов ниже:")
                embed.set_image(url=ORDER_IMAGE_URL)
                button_view = ButtonView()
                await channel.send(embed=embed, view=button_view)
            await asyncio.sleep(300)  # 300 секунд = 5 минут

    bot.loop.create_task(send_initial_message())

@bot.command()
async def закрыть_заказ(ctx):
    embed = Embed(description="Вы хотите оставить отзыв о вашем заказе?")
    view = ui.View(timeout=None)
    view.add_item(ui.Button(style=ButtonStyle.success, label="Да", custom_id="confirm_yes"))
    view.add_item(ui.Button(style=ButtonStyle.danger, label="Нет", custom_id="confirm_no"))

    message = await ctx.send(embed=embed, view=view)

    async def button_callback(interaction: disnake.MessageInteraction):
        if interaction.component.custom_id == "confirm_yes":
            await ask_for_rating(interaction)
        elif interaction.component.custom_id == "confirm_no":
            await archive_channel(interaction.channel, interaction.user)
            await interaction.response.send_message("Ваш заказ был архивирован.", ephemeral=True)

    for item in view.children:
        if isinstance(item, ui.Button):
            item.callback = button_callback

async def ask_for_rating(interaction: disnake.MessageInteraction):
    embed = Embed(description="Пожалуйста, оцените ваш заказ:")
    embed.set_image(url="https://i.imgur.com/s7FQgKF.png")

    view = ui.View(timeout=None)
    stars = ["1⭐", "2⭐", "3⭐", "4⭐", "5⭐"]
    for i, star in enumerate(stars, 1):
        view.add_item(ui.Button(style=ButtonStyle.primary, label=star, custom_id=f"rating_{i}"))

    await interaction.message.edit(embed=embed, view=view)

    async def button_callback(interaction: disnake.MessageInteraction):
        if interaction.component.custom_id.startswith("rating_"):
            rating = int(interaction.component.custom_id.split("_")[1])
            await interaction.response.send_modal(ReviewModal(rating, interaction.user, interaction.channel))

    for item in view.children:
        if isinstance(item, ui.Button):
            item.callback = button_callback

class ReviewModal(ui.Modal):
    def __init__(self, rating, user, channel):
        self.rating = rating
        self.user = user
        self.channel = channel
        components = [
            ui.TextInput(
                label="Ваш отзыв",
                placeholder="Напишите ваш отзыв здесь...",
                style=disnake.TextInputStyle.paragraph,
                custom_id="review_text"
            )
        ]
        super().__init__(title=f"Оценка {self.rating} ⭐", components=components)

    async def callback(self, interaction: ModalInteraction):
        review_text = interaction.text_values['review_text']
        await interaction.response.send_message("Ваш отзыв был получен. Ожидайте подтверждения.", ephemeral=True)
        
        # Запросить изображение у персонала
        embed = Embed(description="Пожалуйста, предоставьте изображение для отзыва:")
        staff_message = await self.channel.send(embed=embed)

        def check(m):
            return m.author.guild_permissions.manage_channels and m.attachments

        staff_response = await bot.wait_for('message', check=check)
        image_url = staff_response.attachments[0].url
        
        # Скачивание изображения и сохранение его локально
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    img_data = await resp.read()
                    with open(f"{self.channel.id}_review_image.png", 'wb') as f:
                        f.write(img_data)

        # Отправка изображения в специальный канал
        storage_channel = bot.get_channel(1250102341290557611)
        storage_message = await storage_channel.send(file=disnake.File(f"{self.channel.id}_review_image.png"))
        stored_image_url = storage_message.attachments[0].url
        
        # Удаление локально сохраненного файла
        os.remove(f"{self.channel.id}_review_image.png")
        
        # Отправка отзыва с URL изображения из специального канала
        review_embed = Embed(title="Отзыв о заказе", color=0xFFD700)
        review_embed.add_field(name="Оценка", value=f"{self.rating} ⭐")
        review_embed.add_field(name="Отзыв", value=review_text)
        review_embed.set_image(url=stored_image_url)
        review_embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)

        review_channel = bot.get_channel(REVIEWS_CHANNEL_ID)
        await review_channel.send(embed=review_embed)
        
        # Переименование канала и удаление доступа клиента
        await archive_channel(self.channel, self.user)


async def archive_channel(channel, user):
    # Assign the completed order role to the user
    role = channel.guild.get_role(COMPLETED_ORDER_ROLE_ID)
    if role:
        await user.add_roles(role)

    # Rename the channel and move it to the archive category
    await channel.edit(name=f"архив-{user.name}")
    await channel.edit(category=bot.get_channel(1246213131429085298))
    await channel.set_permissions(user, read_messages=False)

bot.run(TOKEN)