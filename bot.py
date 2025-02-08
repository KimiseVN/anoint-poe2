import discord
import pandas as pd
import os

# Đọc dữ liệu từ file Excel
data = pd.read_excel("AnointList.xlsx")

# Loại bỏ khoảng trắng thừa và chuyển tất cả tên skill trong cột 'NotablePassive' về chữ thường
data['NotablePassive'] = data['NotablePassive'].str.strip().str.lower()
data['DistilledEmotions'] = data['DistilledEmotions'].str.strip()  # Nếu cần, có thể áp dụng .str.strip() cho cột DistilledEmotions nếu có khoảng trắng thừa
data['AnointEffects'] = data['AnointEffects'].str.strip()  # Nếu cần, có thể áp dụng .str.strip() cho cột AnointEffects nếu có khoảng trắng thừa

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

# Sự kiện khi bot nhận tin nhắn
@bot.event
async def on_message(message):
    # Tránh bot phản hồi chính nó
    if message.author == bot.user:
        return

    # Kiểm tra nếu tin nhắn được gửi từ đúng kênh
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return  # Không xử lý tin nhắn nếu không phải kênh được chỉ định

    # Xử lý tin nhắn văn bản (tìm skill theo tên)
    skill_name = message.content.strip().lower()  # Loại bỏ khoảng trắng và chuyển thành chữ thường
    print(f'Người dùng nhập: {skill_name}')  # Debugging: In ra tên skill người dùng nhập

    # Tìm skill trong toàn bộ cột "NotablePassive" (kiểm tra phần tử con trong tên)
    skill_info = data[data['NotablePassive'].str.contains(skill_name, case=False, na=False)]  # Tìm kiếm không phân biệt chữ hoa/chữ thường

    # Kiểm tra nếu tìm thấy skill
    if not skill_info.empty:
        # Tạo phản hồi với tất cả kết quả tìm được
        response = ""
        count = 0
        for index, row in skill_info.iterrows():
            distilled_emotions = row["DistilledEmotions"]
            anoint_effects = row["AnointEffects"]

            # Thêm thông tin của mỗi skill vào phản hồi
            response += (
                f'**{row["NotablePassive"].capitalize()}**\n'
                f'💬 **Distilled Emotions:** {distilled_emotions}\n'
                f'⚡ **Anoint Effects:** {anoint_effects}\n\n'
            )

            count += 1
            # Nếu tin nhắn quá dài (> 2000 ký tự), gửi nó và tạo phản hồi mới
            if len(response) > 2000:
                await message.channel.send(response)
                response = ""  # Reset lại phản hồi sau khi gửi
                count = 0

        # Gửi tin nhắn còn lại nếu có
        if response:
            await message.channel.send(response)
    else:
        await message.channel.send("Không tìm thấy thông tin cho skill này.")

# Lấy token từ biến môi trường
discord_token = os.getenv('DISCORD_TOKEN')

# Chạy bot
if discord_token:
    bot.run(discord_token)
else:
    print("Không tìm thấy Discord Token trong biến môi trường.")
