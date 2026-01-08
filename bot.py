import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = "kcmd-wiki/resources-publisher"


class PostBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=[], intents=intents)

    async def setup_hook(self):
        MY_GUILD = discord.Object(id=625360381673472065) # 본인 서버 ID
        self.tree.clear_commands(guild=None)
        await self.tree.sync() 
        menu = app_commands.ContextMenu(
            name='KCMD-WIKI에 게시/업데이트',
            callback=self.publish_to_web
        )
        self.tree.add_command(menu, guild=MY_GUILD) # 특정 길드에만 추가
        synced = await self.tree.sync(guild=MY_GUILD)
        print(f"동기화 완료! {len(synced)}개의 커맨드가 등록됨")

    async def publish_to_web(self, interaction: discord.Interaction, message: discord.Message):
        if interaction.user.id != message.author.id:
            await interaction.response.send_message("❌ 본인의 메시지만 게시할 수 있습니다.", ephemeral=True)
            return

        await interaction.response.send_message("🚀 데이터를 전송 중입니다...", ephemeral=True)

        print(message.id)
        print(message.content)
        success = await self.sync_with_github(message)

        if success:
            await interaction.edit_original_response(content="✅ 웹사이트에 성공적으로 게시/업데이트되었습니다!")
        else:
            await interaction.edit_original_response(content="❌ 게시 중 오류가 발생했습니다.")

    async def sync_with_github(self, message: discord.Message):
        url = f"https://api.github.com/repos/{REPO_NAME}/dispatches"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "event_type": "publish_post",  # 액션에서 식별할 이름
            "client_payload": {
                "filename": str(message.id),
                "content": message.content
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                return resp.status == 204 # 성공 시 204 No Content 반환

bot = PostBot()
bot.run(DISCORD_BOT_TOKEN)



