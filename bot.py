import discord
import pandas as pd
import os

# Đọc dữ liệu từ file Excel
data = pd.read_excel("Anointlist.xlsx")

# Đếm số lượng Notable Passive
notable_passive_count = len(data['Notable Passive'].dropna())  # Đếm số lượng dòng có dữ liệu trong cột 'Notable Passive'

# Tạo bot với intents để lắng nghe tin nhắn
intents = discord.Intents.default()
intents.messages = True  # Đảm bảo bot có thể lắng nghe các tin nhắn
bot = discord.Client(intents=intents)

# Đặt ID kênh mà bot sẽ hoạt động
ALLOWED_CHANNEL_ID = 1337773283860545546

# Sự kiện khi bot đã sẵn sàng
@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập như {bot.user}')
    print(f'Có {notable_passive_count} Notable Passive đã được nhập vào.')

    # Thông báo trên Discord rằng bot đã được khởi động và có bao nhiêu Notable Passive được nhập vào
    channel = bot.get_channel(ALLOWED_CHANNEL_ID)  # Lấy kênh dựa trên ID
    if channel:
        await channel.send(f'Bot đã được khởi động! Có tổng cộng {notable_passive_count} Notable Passive đã được nhập vào.')

# Sự kiện khi bot nhận tin nhắn
@bot.event
async def on_message(message):
    # Tránh bot phản hồi chính nó
    if message.author == bot.user:
        return

    # Kiểm tra nếu tin nhắn được gửi từ đúng kênh
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return  # Không xử lý tin nhắn nếu không phải kênh được chỉ định

    # Kiểm tra nếu tin nhắn có chứa tên Notable Passive
    notable_passive = message.content.strip()
    
    # Tìm kiếm tên Notable Passive trong dữ liệu
    row = data[data['Notable Passive'] == notable_passive]
    
    if not row.empty:
        # Trả về kết quả tương ứng từ các cột Distilled Emotions và Anoint Effects
        distilled_emotions = row['Distilled Emotions'].values[0]
        anoint_effects = row['Anoint Effects'].values[0]
        
        await message.channel.send(f"Distilled Emotions: {distilled_emotions}\nAnoint Effects: {anoint_effects}")
    else:
        await message.channel.send("Không tìm thấy thông tin cho Notable Passive này.")

# Lấy token từ biến môi trường
discord_token = os.getenv('DISCORD_TOKEN')

# Chạy bot
if discord_token:
    bot.run(discord_token)
else:
    print("Không tìm thấy Discord Token trong biến môi trường.")
