#製作人為@nomi_im @arukudaisuki 所有,請勿侵犯智慧財產權,參考和使用請註記並詢問作者
import os
import datetime
import discord
from discord import option
from discord.ext import commands

#開啟特殊權限(privileged intents)還有反應跟管理成員
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.voice_states = True
intents.guilds = True

#指令前綴(!hello可以回復等)
bot = commands.Bot(command_prefix="!",intents=intents)

#設定全域變數
emoji_rules = {}
guild_id = {}

#設定LOG檔案
forder = os.path.dirname(os.path.abspath(__file__)) #找到資料夾
file = os.path.join(forder,"log.txt") #新增檔案
def write_log(guild : int,text : str):
    if not os.path.exists(file):
        with open(file, "w",encoding="utf-8") as logfile:
            logfile.write("###beginning###\n")
    with open(file, "a",encoding="utf-8") as logfile:
        time = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
        logfile.write(f"[{guild}][{time}]{text}\n")

#指令內部
@bot.command()
async def hello(ctx):
    await ctx.send("你好")
    write_log(ctx.guild.id,f"{ctx.author}使用了!hello")

#斜線指令(name為斜線指令的名稱,description為斜線指令的敘述,option是訊息的參數)然後role是身分組
@bot.slash_command(name="set_role_message",description="新增新增訊息反應給身份組")
@option("message_id",description="想要新增反應的訊息ID",type = str)
@option("emoji",description="反應",type = str)
@option("role",description="身分組",type = discord.Role)
async def set_role_message(ctx,message_id,emoji,role):
    channel = ctx.channel #讀取訊息頻道
    message = await channel.fetch_message(int(message_id))
    await message.add_reaction(emoji)
    emoji_rules[int(message_id)] = {"emoji": emoji,"role_id": role.id}
    await ctx.respond("我設定好了!")
    write_log(ctx.guild.id,f"{ctx.author}使用了set_role_message")
##反應回饋身分組(payload是反應回饋(成員身分和頻道跟訊息ID和反應內容))
@bot.event
async def on_raw_reaction_add(payload):
    data = emoji_rules.get(payload.message_id) #從新增反應的訊息抓取斜線指令的資料
    if data is None:
        return
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    role = guild.get_role(data["role_id"])
    if member is None or member.bot: #如果按反應的人不在伺服器裡面或者它是機器人就return
        return
    if data is None: #如果資料是空的就return
        return
    if str(payload.emoji) == data["emoji"]:
        await member.add_roles(role)
##反應取消身分組
@bot.event
async def on_raw_reaction_remove(payload):
    data = emoji_rules.get(payload.message_id)
    if data is None:
        return
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    role = guild.get_role(data["role_id"])
    if member is None or member.bot:
        return
    if data is None:
        return
    if str(payload.emoji) == data["emoji"]:
        await member.remove_roles(role)
   
#給予身分組
@bot.slash_command(name="role_add", description="給予身分組(限管理員）")
@option("dc_member",description="給予身分組的dc成員" ,type=discord.Member)
@option("dc_role",description="給予的身分組",type = discord.Role)
async def role_add(interaction : discord.Interaction,dc_member,dc_role): #interaction是斜線指令的詳細資料
    if not interaction.author.guild_permissions.administrator:
        await interaction.resopnd("你不是管理員", ephemeral=True)
        write_log(interaction.guild.id,f"{interaction.author}對{dc_member}使用了role_add,但沒有權限")
        return
    try:
        await dc_member.add_roles(dc_role)
        await interaction.respond(f"已賦予身分組給{dc_member}")
        write_log(interaction.guild.id,f"{interaction.author}對{dc_member}使用了role_add,加上了{dc_role}身分組")
    except discord.errors.Forbidden:
         await interaction.respond("您沒有權限",ephemeral=True)
    except :
        await interaction.respond("Error", ephemeral=True)
#移除身分組
@bot.slash_command(name="role_remove", description="移除身分組(限管理員）")
@option("dc_member",description="移除身分組的dc成員" ,type=discord.Member)
@option("dc_role",description="移除的身分組",type = discord.Role)
async def role_remove(interaction : discord.Interaction,dc_member,dc_role):
    if not interaction.author.guild_permissions.administrator:
        await interaction.resopnd("你不是管理員", ephemeral=True)
        write_log(interaction.guild.id,f"{interaction.author}對{dc_member}使用了role_remove,但沒有權限")
        return
    try:
        await dc_member.remove_roles(dc_role)
        await interaction.respond(f"已移除{dc_member}身分組")
        write_log(interaction.guild.id,f"{interaction.author}對{dc_member}使用了role_remove,移除了{dc_role}身分組")
    except discord.errors.Forbidden:
         await interaction.respond("您沒有權限",ephemeral=True)
    except :
        await interaction.respond("Error", ephemeral=True)
    
#歡迎身分組
@bot.slash_command(name="welcome_message",description="留言給身分組")
@option("channel_id",description="頻道ID")
@option("message",description="設定訊息",type = str)
@option("role",description="選取身分組",type = discord.Role)
async def welcome_message(ctx,message,role):
    await ctx.respond("我還沒做好")

#監控誰進出了語音房(before跟after是語音房狀態的變動前跟變動後資料)
@bot.slash_command(name="member_state_voice",description="設定成員加入訊息在本頻道")
@option("boolin",description="True/False",type = bool)
async def member_voice_state(interaction : discord.Interaction,boolin):
    guide_identify = int(interaction.guild.id)
    if not interaction.author.guild_permissions.administrator:
        interaction.respond("管理員才可以設置!")
        write_log(interaction.guild.id,f"{interaction.author}使用了member_state_voice,但沒有權限")
        return
    else :
        send_vce_channel = interaction.channel
        voice_channel_event = bool(boolin)
        guild_id[guide_identify] = {"channel": send_vce_channel,"bool": voice_channel_event}
        if not voice_channel_event:
            await interaction.respond("已經取消設定了!")
            write_log(interaction.guild.id,f"{interaction.author}在{send_vce_channel}關閉了member_state_voice")
        elif voice_channel_event:
            await interaction.respond("已經設定好了!")
            write_log(interaction.guild.id,f"{interaction.author}在{send_vce_channel}開啟了member_state_voice")
        else :
            await interaction.respond("設定錯誤")
#進出語音室反應
@bot.event
async def on_voice_state_update(member, before, after):
    guild = int(member.guild.id)
    data = guild_id.get(guild)
    if data is None:
        return
    channel_event = data["bool"]
    if channel_event == False:
        return
    if before.channel != after.channel: #如果語音房狀態有變動
        channel = data["channel"]
        if after.channel is not None and before.channel is None:
            await channel.send(f"{member.display_name}加入了 {after.channel.name} ")
        elif after.channel is not None and before.channel is not None:
            await channel.send(f"{member.display_name}離開了 {before.channel.name} ,加入了 {after.channel.name} ")
        elif after.channel is None and before.channel is not None:
            await channel.send(f"{member.display_name}離開了 {before.channel.name} ")
        else :
            await channel.send("error")

#查看自身位置
@bot.slash_command(name="whereami",description="查詢自身位置伺服器跟頻道ID")
async def whereami(interaction : discord.Interaction):
    channel_ID = interaction.channel.id
    guild_ID = interaction.guild.id
    await interaction.respond(f"伺服器ID為 {guild_ID} ,頻道ID為 {channel_ID} ,請勿隨便轉傳")
    write_log(interaction.guild.id,f"{interaction.author}在伺服器ID:{guild_ID},頻道ID:{channel_ID}使用了whereami")

#自身是否為管理員
@bot.slash_command(name="checking_administrator",description="是否為管理員")
async def checking_administrator(ctx : discord.ApplicationContext):
    if ctx.author.guild_permissions.administrator:
        await ctx.respond("你是管理員")
    else:
        await ctx.respond("你不是管理員")

##反應回饋身分組(payload是反應回饋(成員身分和頻道跟訊息ID和反應內容))

#help
help_message = """
command:
!hello 回復你好
Slash_Commands:
help [指令] 查詢各種指令
set_role_message [訊息ID] [反應] [身分組] 設定反應身分組 "log"
role_add [成員] [身分組] 對成員增加身分組 "log"
role_remove [成員] [身分組] 對成員移除身分組 "log"
checking_administator 查看自身是否為管理員
whereami 查詢自身位置伺服器跟頻道ID "log"
member_state_voice [True/False] 在本頻道傳送誰進入/離開語音房 "log"
welcome_rule [設定訊息] [選取身分組] 在本頻道傳送特定訊息會被添加身分組
"""

@bot.slash_command(name="help",description="取得指令幫助")
@option("help_command",description="查詢指令",require = False,default = None)
async def help(ctx,help_command:str = None):
    if help_command is None:
        await ctx.respond(f"```{help_message}```")
    elif help_command is set_role_message:
        await ctx.respond("我沒被設定")
    elif help_command is role_add:
        await ctx.respond("我沒被設定")
    elif help_command is role_remove:
        await ctx.respond("我沒被設定")
    elif help_command is welcome_message:
        await ctx.respond("我沒被設定")
    else :
        await ctx.respond("指令錯誤或者不存在")

#啟動機器人(指令結尾)
#region Bot token
bot.run("MTM3Mzk1NzcwMjE5NTIxNjM5NA.GsaK-s.6vob3vQeMhnX0UPjcpAnRciWYJgK_7-_aF6lRg")
#endregion 