import os
import discord
import pandas as pd
import pytesseract
from PIL import Image
import requests
from io import BytesIO
from discord.ext import commands

# Lấy Token từ biến môi trường
TOKEN = os.getenv("DISCORD_TOKEN")

# ID của kênh được phép bot hoạt động (Thay bằng ID kênh Discord thực tế)
ALLOWED_CHANNEL_ID = 1337773283860545546  # Cập nhật Channel ID của bạn

# Tên file dữ liệu Excel
EXCEL_FILE = "AnointList.xlsx"

# Kiểm tra và tạo file Excel nếu chưa tồn tại
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Name", "Type", "Effects"])
    df.to_excel(EXCEL_FILE, index=False)
    print("✅ Đã tạo file AnointList.xlsx")

# Load dữ liệu từ file Excel
def load_data():
    return pd.read_excel(EXCEL_FILE).fillna("")

data = load_data()

# Thiết lập intents cho bot
intents = discord.Intents.default()
intents.message_content = True

# Khởi tạo bot với prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot đã kết nối với Discord! Logged in as {bot.user}')
    print(f'🔹 Tổng số Skill hiện tại: {len(data)}')

@bot.event
async def on_message(message):
    """Xử lý tin nhắn và tìm skill theo tên hoặc ảnh"""
    if message.author == bot.user or message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # Xử lý tin nhắn văn bản (tìm skill theo tên)
    skill_name = message.content.strip().lower()
    skill_info = data[data["Name"].str.strip().str.lower() == skill_name]

    if not skill_info.empty:
        skill_type = skill_info.iloc[0]["Type"]
        skill_effect = skill_info.iloc[0]["Effects"]

        response = (
            f'**{skill_name.capitalize()}**\n'
            f'📜 **Distilled:**\n{skill_type}\n'
            f'✅ **Effect:**\n{skill_effect}'
        )
        await message.channel.send(response)

    # Xử lý ảnh nếu có ảnh đính kèm
    elif message.attachments:
        await process_image(message, message.attachments[0])

    # Nếu không phải lệnh và không tìm thấy skill
    elif not message.content.startswith("!"):
        await message.channel.send("❌ Không tìm thấy Skill! Kiểm tra lại xem đã nhập đúng chưa.")

    # Xử lý lệnh bot
    await bot.process_commands(message)

async def process_image(message, attachment):
    """Trích xuất skill từ ảnh bằng Tesseract OCR"""
    try:
        img_url = attachment.url
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))

        extracted_text = pytesseract.image_to_string(img)
        print(f"OCR Extracted Text: {extracted_text}")  # Debugging

        found_skills = []
        for skill in data["Name"]:
            if skill.lower() in extracted_text.lower():
                found_skills.append(skill)

        if found_skills:
            response_text = "**🔍 Skill phát hiện trong ảnh:**\n"
            for skill in found_skills:
                skill_info = data[data["Name"] == skill].iloc[0]
                skill_type = skill_info["Type"]
                skill_effect = skill_info["Effects"]

                response_text += (
            f'**{skill_name.capitalize()}**\n'
            f'📜 **Distilled:**\n{skill_type}\n'
            f'✅ **Effect:**\n{skill_effect}'
                )
            await message.channel.send(response_text)
        else:
            await message.channel.send("⚠️ Không tìm thấy Skill nào trong ảnh!")

    except Exception as e:
        await message.channel.send(f"❌ Lỗi xử lý ảnh: {str(e)}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 100):
    """Xóa toàn bộ tin nhắn trong kênh Chatbot"""
    if ctx.channel.id == ALLOWED_CHANNEL_ID:
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(f"🧹 **Đã xóa {len(deleted)} tin nhắn trong kênh này!**", delete_after=5)
        except discord.Forbidden:
            await ctx.send("❌ Bot không có quyền xóa tin nhắn! Hãy kiểm tra quyền 'Manage Messages'.")
        except discord.HTTPException:
            await ctx.send("❌ Lỗi khi xóa tin nhắn! Hãy thử lại sau.")
    else:
        await ctx.send("❌ Lệnh này chỉ có thể sử dụng trong kênh được chỉ định.")

bot.run(TOKEN)
