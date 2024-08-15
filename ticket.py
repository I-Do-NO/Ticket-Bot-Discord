import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
import asyncio
import json

TOKEN = '' # inja token ton ro bezarid
COUNTERS_FILE = 'counters.json'

intents = discord.Intents.default()
intents.message_content = True  
intents.reactions = True 

bot = commands.Bot(command_prefix="!", intents=intents)

def load_counters():
    try:
        with open(COUNTERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"support": 0, "sales": 0, "feedback": 0}

def save_counters(counters):
    with open(COUNTERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(counters, f, ensure_ascii=False, indent=4)

counters = load_counters()

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="پشتیبانی", value="support", emoji="🛠️"),
            discord.SelectOption(label="خرید", value="sales", emoji="🛒"),
            discord.SelectOption(label="ایده", value="feedback", emoji="💡")
        ]
        super().__init__(placeholder="یک دسته‌بندی انتخاب کنید...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        guild = interaction.guild

        category_dict = {
            "support": "پشتیبانی",
            "sales": "خرید",
            "feedback": "ایده"
        }
        
        category_name_farsi = category_dict.get(category_name, category_name)
        category = discord.utils.get(guild.categories, name=category_name_farsi)

        if category is None:
            category = await guild.create_category(category_name_farsi)
            print(f'Created category: {category_name_farsi}')  

        counters[category_name] += 1
        save_counters(counters)
 
        channel_name = f'ticket-{category_name}-{counters[category_name]:03}'
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            channel_name,
            overwrites=overwrites,
            category=category
        )

        msg = await channel.send(
            f', {interaction.user.mention} Chetor Mitoim Be Shoma Komak Konim\n'
            'Lotfan Kasi Ro Mention Nakonid Ta Team Modiriyati Be SHoma Pasokh Bde. React with 🗑️ to close this ticket.'
        )
        await msg.add_reaction("🗑️")

        await interaction.response.send_message(f'Ticket created: {channel.mention}', ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__()
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    change_status.start()
    print(f'Logged in as {bot.user}')

@bot.command()
async def ticket(ctx):
    view = TicketView()
    await ctx.send("لطفاً یک دسته‌بندی برای تیکت خود انتخاب کنید:", view=view)

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if reaction.emoji == "🗑️" and not user.bot:
        message = reaction.message
        channel = message.channel

        if channel.name.startswith('ticket-'):
            bot_reactions = [r for r in message.reactions if str(r.emoji) == "🗑️" and r.me]
            user_reactions = [r for r in message.reactions if str(r.emoji) == "🗑️" and r.count > 1]

            if bot_reactions and user_reactions:
                await channel.delete()
                print(f'Deleted channel {channel.name}')  

bot.run(TOKEN)
