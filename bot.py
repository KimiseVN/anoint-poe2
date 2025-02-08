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

# Lệnh !clear để xóa lịch sử tin nhắn trong kênh
@bot.event
async def on_message(message):
    # Tránh bot phản hồi chính nó
    if message.author == bot.user:
        return

    # Kiểm tra nếu tin nhắn được gửi từ đúng kênh
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return  # Không xử lý tin nhắn nếu không phải kênh được chỉ định

    # Lệnh !clear để xóa tin nhắn trong kênh
    if message.content.startswith("!clear"):
        # Kiểm tra quyền hạn của người gửi tin nhắn (đảm bảo họ có quyền xóa tin nhắn)
        if message.author.guild_permissions.manage_messages:
            # Xóa tất cả tin nhắn trong kênh (có thể chỉ xóa một số lượng nhất định nếu muốn)
            await message.channel.purge(limit=100)  # Thay 100 bằng số lượng tin nhắn bạn muốn xóa
            await message.channel.send("Lịch sử tin nhắn đã được xóa!", delete_after=5)  # Thông báo và xóa sau 5 giây
        else:
            await message.channel.send("Bạn không có quyền xóa tin nhắn trong kênh này.")

    # Xử lý tin nhắn văn bản (tìm skill theo tên)
    skill_name = message.content.strip().lower()  # Loại bỏ khoảng trắng và chuyển thành chữ thường
    print(f'Người dùng nhập: {skill_name}')  # Debugging: In ra tên skill người dùng nhập

    # Tìm skill trong toàn bộ cột "NotablePassive" (kiểm tra phần tử con trong tên)
    skill_info = data[data['NotablePassive'].str.contains(skill_name, case=False, na=False)]  # Tìm kiếm không phân biệt chữ hoa/chữ thường

    # Kiểm tra nếu tìm thấy skill
    if not skill_info.empty:
        # Tạo phản hồi với tất cả kết quả tìm được
        response = ""
        for index, row in skill_info.iterrows():
            distilled_emotions = row["DistilledEmotions"]
            anoint_effects = row["AnointEffects"]

            # Thêm thông tin của mỗi skill vào phản hồi
            response += (
                f'**{row["NotablePassive"].capitalize()}**\n'
                f'💬 **Distilled Emotions:** {distilled_emotions}\n'
                f'⚡ **Anoint Effects:** {anoint_effects}\n\n'
            )
        
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
