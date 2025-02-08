import discord
import pandas as pd
import os

# Đọc dữ liệu từ file AnointList.xlsx và nhập vào data
data = pd.read_excel("AnointList.xlsx")

# Loại bỏ khoảng trắng thừa và chuyển tất cả tên skill trong cột 'Name' về chữ thường
data['Name'] = data['Name'].str.strip().str.lower()
data['Distilled'] = data['Distilled'].str.strip()  # Loại bỏ khoảng trắng thừa trong cột Distilled
data['Effects'] = data['Effects'].str.strip()  # Loại bỏ khoảng trắng thừa trong cột Effects

# Đếm số lượng skill được nhập vào
num_skills = len(data)  # Đếm tổng số dòng trong file Excel

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
    print(f'Đã nhập {num_skills} Skill vào dữ liệu.')

    # Thông báo trên Discord rằng bot đã nhập bao nhiêu Skill vào dữ liệu
    channel = bot.get_channel(ALLOWED_CHANNEL_ID)  # Lấy kênh dựa trên ID
    if channel:
        await channel.send(f'Bot đã được khởi động! Đã nhập tổng cộng {num_skills} Skill vào dữ liệu.')

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

    # Tìm skill trong toàn bộ cột "Name" (kiểm tra phần tử con trong tên)
    skill_info = data[data['Name'].str.contains(skill_name, case=False, na=False)]  # Tìm kiếm không phân biệt chữ hoa/chữ thường

    # Kiểm tra nếu tìm thấy skill
    if not skill_info.empty:
        # Tạo phản hồi với tất cả kết quả tìm được
        response = ""
        count = 0
        for index, row in skill_info.iterrows():
            distilled_emotions = row["Distilled"]
            anoint_effects = row["Effects"]

            # Thêm thông tin của mỗi skill vào phản hồi
            response += (
                f'**{row["Name"].capitalize()}**\n'
                f'💬 **Distilled:** {distilled_emotions}\n'
                f'⚡ **Effects:** {anoint_effects}\n\n'
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
