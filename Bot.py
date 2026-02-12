import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------ WHITELIST ------------------
WHITELIST = [
    1256288026863206556,  # Sen
    1432718486203007100,  # Alperen
    1267973192572600341,  # Mehmet
    1218464018168152084   # Wupzi
]

# ------------------ TAM YASAK SUNUCULAR ------------------
TARGET_GUILDS = [
    1459613444495114337,
    1455320048574009434,
    1459997366047215774
]

# ------------------ READY ------------------
@bot.event
async def on_ready():
    print(f"{bot.user} aktif!")

# ------------------ YARDIM ------------------
@bot.command(name="yardım")
async def yardim(ctx):
    embed = discord.Embed(
        title="📜 Komut Listesi",
        description="""
**Herkes Kullanabilir**
- `!sunucu-bilgi` : Sunucu hakkında bilgi verir.
- `!yardım` : Bu komut listesini gösterir.

**Yönetici Kullanabilir**
- `!ban <@kullanıcı veya kullanıcı_id> <sebep>` : Kullanıcıyı banlar ve DM gönderir.
- `!kick <@kullanıcı veya kullanıcı_id> <sebep>` : Kullanıcıyı atar ve DM gönderir.
- `!dm <@kullanıcı veya kullanıcı_id> <mesaj>` : Belirtilen kullanıcıya DM gönderir.
- `!dms <mesaj>` : Sunucudaki herkese DM atar (rate-limitli).
- `!duyuru <kanal_id> <mesaj>` : Belirlenen kanala duyuru mesajı atar.

**Whitelist Kullanabilir**
- `!tam-yasak <kullanıcı_id>` : Belirlenen sunucularda kullanıcıyı yasaklar.
        """,
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# ------------------ SUNUCU BILGI ------------------
@bot.command(name="sunucu-bilgi")
async def sunucu_bilgi(ctx):
    guild = ctx.guild
    mesaj = f"""
📌 Sunucu Adı: {guild.name}
👑 Sahip: {guild.owner}
👥 Üye Sayısı: {guild.member_count}
🆔 Sunucu ID: {guild.id}
📅 Oluşturulma: {guild.created_at.strftime("%d/%m/%Y")}
"""
    await ctx.send(f"```{mesaj}```")

# ------------------ BAN ------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, sebep="Sebep belirtilmedi"):
    try:
        await member.send(
            f"{ctx.guild.name} den {ctx.author} tarafından Yasaklandın.\nSebep: {sebep}"
        )
    except:
        pass
    await member.ban(reason=sebep)
    mesaj = f"""
KULLANICI BANLANDI
Kullanıcı: {member}
Yetkili: {ctx.author}
Sebep: {sebep}
"""
    await ctx.send(f"```{mesaj}```")

# ------------------ KICK ------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, sebep="Sebep belirtilmedi"):
    try:
        await member.send(
            f"{ctx.guild.name} den {ctx.author} tarafından Atıldın.\nSebep: {sebep}"
        )
    except:
        pass
    await member.kick(reason=sebep)
    mesaj = f"""
KULLANICI ATILDI
Kullanıcı: {member}
Yetkili: {ctx.author}
Sebep: {sebep}
"""
    await ctx.send(f"```{mesaj}```")

# ------------------ DM ------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def dm(ctx, member: discord.User, *, mesaj):
    try:
        await member.send(mesaj)
        await ctx.send(f"✅ Mesaj başarıyla {member} adlı kullanıcıya gönderildi.")
    except:
        await ctx.send("❌ Kullanıcıya DM gönderilemedi.")

# ------------------ DMS (HERKESE DM, RATE-LIMITLI) ------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def dms(ctx, *, mesaj):
    count = 0
    for member in ctx.guild.members:
        if member.bot:
            continue
        try:
            await member.send(mesaj)
            count += 1
            await asyncio.sleep(5)  # 5 saniye bekle, rate limit için
        except:
            continue
    await ctx.send(f"✅ Mesaj gönderimi tamamlandı. Toplam DM gönderilen kişi sayısı: {count}")

# ------------------ DUYURU ------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def duyuru(ctx, kanal_id: int, *, mesaj):
    kanal = bot.get_channel(kanal_id)
    if kanal:
        await kanal.send(f"📢 DUYURU\n{mesaj}")
        await ctx.send("✅ Duyuru gönderildi.")
    else:
        await ctx.send("❌ Kanal bulunamadı.")

# ------------------ TAM YASAK ------------------
@bot.command(name="tam-yasak")
async def tam_yasak(ctx, user_id: int):
    if ctx.author.id not in WHITELIST:
        return await ctx.send("```Bu komutu kullanma yetkin yok.```")
    banned_count = 0
    for guild in bot.guilds:
        if guild.id in TARGET_GUILDS:
            try:
                user = await bot.fetch_user(user_id)
                try:
                    await user.send(
                        f"{guild.name} den {ctx.author} tarafından Yasaklandın.\nSebep: Global Yasak"
                    )
                except:
                    pass
                await guild.ban(user, reason="Global Yasak")
                banned_count += 1
            except:
                continue
    await ctx.send(f"```Tam Yasak İşlemi Tamamlandı.\nToplam Yasaklanan Sunucu: {banned_count}```")

# ------------------ HATA MESAJLARI ------------------
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için Yönetici iznine sahip olmalısın.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre girdin. Kullanım: !ban <@kullanıcı> <sebep>")
    else:
        await ctx.send("❌ Bir hata oluştu. Lütfen tekrar dene.")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için Yönetici iznine sahip olmalısın.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre girdin. Kullanım: !kick <@kullanıcı> <sebep>")
    else:
        await ctx.send("❌ Bir hata oluştu. Lütfen tekrar dene.")

@dm.error
async def dm_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için Yönetici iznine sahip olmalısın.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre girdin. Kullanım: !dm <@kullanıcı veya kullanıcı_id> <mesaj>")
    else:
        await ctx.send("❌ Bir hata oluştu. Kullanıcıya mesaj gönderilemedi.")

@dms.error
async def dms_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için Yönetici iznine sahip olmalısın.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre girdin. Kullanım: !dms <mesaj>")
    else:
        await ctx.send("❌ Bir hata oluştu. Mesaj gönderilemedi.")

@duyuru.error
async def duyuru_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için Yönetici iznine sahip olmalısın.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre girdin. Kullanım: !duyuru <kanal_id> <mesaj>")
    else:
        await ctx.send("❌ Bir hata oluştu. Duyuru gönderilemedi.")

# ------------------ BOTU ÇALIŞTIR ------------------
bot.run(os.environ["TOKEN"])
