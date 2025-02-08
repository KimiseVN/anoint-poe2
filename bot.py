import discord
import pandas as pd
import os

# Đọc dữ liệu từ file Excel
data = pd.read_excel("AnointList.xlsx")

# Tạo bot với intents để lắng nghe tin nhắn
intents = discord.Intents.default()
intents.messages = True  # Đảm bảo bot có thể lắng nghe các tin nhắn
bot = discord.Client(intents=intents)

# Sự kiện khi bot đã sẵn sàng
@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập như {bot.user}')

# Sự kiện khi bot nhận tin nhắn
@bot.event
async def on_message(message):
    # Tránh bot phản hồi chính nó
    if message.author == bot.user:
        return

    # Kiểm tra nếu tin nhắn có chứa tên Notable Passive
    notable_passive = message.content.strip()
    
    # Tìm kiếm tên Notable Passive trong dữ liệu
    row = data[data['Notable Passive'] == notable_passive]
    
    if not row.empty:
        # Trả về kết quả tương ứng từ các cột Distilled Emotions và Anoint Effects
        distilled_emotions = row['Distilled Emotions'].values[0]
        anoint_effects = row['Anoint Effects'].values[0]
        
        await message.channel.send(f"**Distilled Emotions**: {distilled_emotions}\n**Anoint Effects**: {anoint_effects}")
    else:
        await message.channel.send("Không tìm thấy thông tin cho Notable Passive này.")

# Lấy token từ biến môi trường
discord_token = os.getenv('DISCORD_TOKEN')

# Chạy bot
if discord_token:
    bot.run(discord_token)
else:
    print("Không tìm thấy Discord Token trong biến môi trường.")
