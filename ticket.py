import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
import asyncio
import json

TOKEN = '' # token bot ton ro bearid
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