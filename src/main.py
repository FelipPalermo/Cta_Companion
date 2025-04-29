import discord
from discord.ext import commands
import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import datetime
from mongo import Mongo
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_BOT")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True


# ------ /// Async config /// ------
bot = commands.Bot(command_prefix='!', intents=intents)
scheduler = AsyncIOScheduler()

# ------ /// Create server /// ------
@bot.command("server")
@commands.has_role("CTA MANAGER")
async def server(ctx, *, mensagem):

    partes = [p.strip() for p in mensagem.split(",")]

    if len(partes) != 3:
        await ctx.send("Por favor, insira :\nNome do canal de voz, nome do canal de log e nome do canal de comando, respectivamente!")
        return

    voice_channel_name, voice_log_name, commands_name = partes
    guild_id = str(ctx.guild.id)

    if Mongo.check_exist_sv(str(ctx.guild.id)) : 
        await ctx.send(f"Servidor ***{ctx.guild.name}***, já esta registrado!")
        return 
    else : 
        try:
            Mongo.create_server(guild_id, voice_channel_name, voice_log_name, commands_name)
            await ctx.send(f"Servidor registrado com exito : ***{ctx.guild.name}***!")
        except Exception as e:
            await ctx.send(f"Erro ao registrar servidor: {e}")

# ------ /// Change voice channel /// ------ 
@bot.command("change_vc")
@commands.has_role("CTA MANAGER")
async def change_vc(ctx, vc_name) : 

    guild = str(ctx.guild.id)    

    try :
        Mongo.change_voice_channel_name(guild, vc_name)
        await ctx.send(f"Canal de voz atualizado com sucesso! Para : {vc_name}")
    except Exception as e : 
        await ctx.send(f"Erro ao alterar nome do canal de voz : {e}")

# ------ /// Change voice log channel /// ------ 
@bot.command("change_vl")
@commands.has_role("CTA MANAGER")
async def change_vc(ctx, vl_name) : 

    guild = str(ctx.guild.id)    

    try :
        Mongo.change_voice_log_name(guild, vl_name)
        await ctx.send(f"Canal de voz atualizado com sucesso! Para : {vl_name}")
    except Exception as e : 
        await ctx.send(f"Erro ao alterar nome do canal de voz : {e}")


# ------ /// Change commands channel /// ------ 
@bot.command("change_cm")
@commands.has_role("CTA MANAGER")
async def change_vc(ctx, cm_name) : 

    guild = str(ctx.guild.id)    

    try :
        Mongo.change_command_name(guild, cm_name)
        await ctx.send(f"Canal de voz atualizado com sucesso! Para : {cm_name}")
    except Exception as e : 
        await ctx.send(f"Erro ao alterar nome do canal de voz : {e}")


# ------ /// Change manager role /// ------ 
@bot.command("change_mr")
@commands.has_role("CTA MANAGER")
async def change_vc(ctx, mr_name) : 

    guild = str(ctx.guild.id)    

    try :
        Mongo.change_command_name(guild, mr_name)
        await ctx.send(f"Canal de voz atualizado com sucesso! Para : {mr_name}")
    except Exception as e : 
        await ctx.send(f"Erro ao alterar nome do canal de voz : {e}")


# ------ /// Change cta role /// ------ 
@bot.command("change_cr")
@commands.has_role("CTA MANAGER")
async def change_vc(ctx, cta_name) : 

    guild = str(ctx.guild.id)    

    try :
        Mongo.change_command_name(guild, cta_name)
        await ctx.send(f"Canal de voz atualizado com sucesso! Para : {cta_name}")
    except Exception as e : 
        await ctx.send(f"Erro ao alterar nome do canal de voz : {e}")

# ------ /// Create login /// ------
@bot.command("register")
async def register(ctx) : 

    Mongo.register(str(ctx.author.id), ctx.author.name); 
    await ctx.send(f"***{ctx.author.name}***, registrado com sucesso!")

# ------ /// Show abscences /// -------
@bot.command("faltas")
async def faltas(ctx) : 
    await ctx.send(Mongo.show_Absence()) 

# ------ /// Check if user on call has roles /// ------
@bot.event
async def on_voice_state_update(member, before, after):

    role = Mongo.get_server_properties(str(member.guild.id))["cta_role"]
    voice_channel_name = Mongo.get_server_properties(str(member.guild.id))["voice_channel_name"]
    now = datetime.now()

    if after.channel and after.channel.name == voice_channel_name:
        if not before.channel or before.channel.name != voice_channel_name:
            if any(cargo.name == role for cargo in member.roles):

                text_channel_name = Mongo.get_server_properties(str(member.guild.id))["commands_name"]
                voice_log = Mongo.get_server_properties(str(member.guild.id))["voice_log_name"]



                text_channel = discord.utils.get(member.guild.text_channels, name=text_channel_name)
                log_channel = discord.utils.get(member.guild.text_channels, name=voice_log)

                if text_channel and log_channel:
                    await log_channel.send(f"{member.name} logged in **{voice_channel_name}** at **{now.strftime('%d-%m-%y %H:%M')}**!")

                    await asyncio.sleep(60)

                    # Verifica se ainda está no mesmo canal
                    if member.voice and member.voice.channel and member.voice.channel.name == voice_channel_name:
                        await log_channel.send(f"{member.name} has stayed in {voice_channel_name} for the minimum time!")
                    else:
                        await log_channel.send(f"{member.name} left before the minimum time!")
                else:
                    print(f"Canal de texto {text_channel_name} ou {voice_log} não encontrado.")
            else:
                print(f"{member.name} não tem o cargo {role}.")
        else:
            print(f"{member.name} já estava no canal de voz ou apenas iniciou o compartilhamento de tela.")

# ------ /// Private message on time trigger /// ------ 

async def send_dm_to_members(cargo_nome, mensagem):
    # Pega todos os membros do servidor
    for guild in bot.guilds:
        for member in guild.members:
            # Verifica se o membro tem o cargo
            if any(cargo.name == cargo_nome for cargo in member.roles):
                try:
                    await member.send(mensagem)
                except discord.Forbidden:
                    print(f"Não foi possível enviar mensagem para {member.name}")

# Função que agenda o envio da mensagem
def schedule_message(cargo_nome, mensagem, data_hora):
    trigger = DateTrigger(run_date=data_hora) 
    scheduler.add_job(send_dm_to_members, trigger, args=[cargo_nome, mensagem])  

#@bot.command("agendar_menssagem")
async def agendar_mensagem(ctx, cargo_nome, mensagem, data_hora: str):
    try:
        # Conversão de data_hora para datetime
        data_hora_obj = datetime.strptime(data_hora, "%d-%m-%y %H:%M")
        
        # Agendar a mensagem
        schedule_message(cargo_nome, mensagem, data_hora_obj)
        
        await ctx.send(f"Event scheduled for : {data_hora_obj}.\nAll discord users in this server with the \"***cta***\" role will be notified.")
    except ValueError:
        await ctx.send("Formato de data e hora inválido. Use 'dd-mm-yy HH:MM'.")


# ------ /// Create invite link /// ------
async def gerar_link_convite(canal_de_voz):
    convite = await canal_de_voz.create_invite(max_uses=3, unique=True)
    return convite.url

# ------ /// Create event /// ------
@bot.command("cta")
async def criar_evento(ctx, nome, descricao, sala_voz, inicio_str, fim_str):

    command_channel = "cta_commands"

    if ctx.chanel.name != command_channel : 
        await ctx.send(f"Please only use commands in {command_channel}")

    else :  
        inicio = datetime.strptime(inicio_str.strip(), "%d-%m-%y %H:%M")
        fim = datetime.strptime(fim_str.strip(), "%d-%m-%y %H:%M")

        inicio += timedelta(hours=3)
        fim += timedelta(hours=3)

        # Adicionar timezone
        inicio = inicio.replace(tzinfo=discord.utils.utcnow().tzinfo)
        fim = fim.replace(tzinfo=discord.utils.utcnow().tzinfo)

        guild = ctx.guild
        canal_de_voz = discord.utils.get(guild.voice_channels, name=sala_voz)
        invite_link = await gerar_link_convite(canal_de_voz)
        cargo = discord.utils.get(guild.roles, name="cta")

    
        await guild.create_scheduled_event(
            name=nome,
            description=descricao,
            entity_type=discord.EntityType.voice,
            start_time=inicio,
            end_time=fim,
            channel=canal_de_voz,
            privacy_level=discord.PrivacyLevel.guild_only
        )

        Mongo.event_log(str(guild), inicio_str, fim_str)
        await agendar_mensagem(ctx, "cta", descricao, inicio_str)

        await send_dm_to_members("cta", f"{nome}, {descricao}\nWill start : {inicio}.\nIn the channel : {invite_link}")

        await canal_de_voz.set_permissions(cargo, connect=True)  # Permitir que membros com esse cargo entrem
        await canal_de_voz.set_permissions(guild.default_role, connect=False)  # Negar acesso para membros sem o cargo

# ------ /// React to new member with CTA role /// ------
@bot.event
async def on_member_update(before, after):
    # Pegando o cargo "CTA"
    cta_role = discord.utils.get(after.guild.roles, name="cta")

    # Se o membro não tinha o cargo antes, mas agora tem
    if cta_role and cta_role not in before.roles and cta_role in after.roles:
        
        embed = discord.Embed(
            title="📢 Sistema de Verificação de CTA (Call to Action)",
            description=(
                "Este sistema garante a presença de jogadores convocados para conteúdos importantes da guilda. "
                "Se você recebeu a **tag @CTA**, leia com atenção abaixo:"
            ),
            color=0x3498db
        )

        embed.add_field(
            name="📆 Participação Obrigatória",
            value=(
                "Jogadores com a tag @CTA devem comparecer no dia, horário e sala de voz definidos "
                "pelo criador do conteúdo."
            ),
            inline=False
        )

        embed.add_field(
            name="🕒 Verificação Automática",
            value=(
                "O bot monitora automaticamente quem entrou na sala e por quanto tempo permaneceu. "
                "É possível configurar um *tempo mínimo de permanência* (ex: 5 minutos) para validar a presença."
            ),
            inline=False
        )

        embed.add_field(
            name="🚫 Ausências",
            value=(
                "Faltas podem ser registradas e analisadas pela liderança da guilda, com ou sem penalidade, "
                "dependendo das regras internas."
            ),
            inline=False
        )

        embed.add_field(
            name="🔒 Proteção de Dados (LGPD)",
            value=(
                "Nenhum dado sensível é coletado. O sistema armazena apenas:\n"
                "- ID do usuário (anonimizado via hash);\n"
                "- Nome de usuário\n"
                "- Data e hora de entrada e saída da sala;\n"
                "- Tempo de permanência.\n\n"
                "Esses dados são usados *exclusivamente para fins de organização interna da guilda*, "
                "em conformidade com a Lei Geral de Proteção de Dados (LGPD)."
            ),
            inline=False
        )

        embed.add_field(
            name="❗ Dúvidas ou problemas?",
            value="Fale com um oficial .",
            inline=False
        )

        embed.set_footer(
            text="Leia com atenção as informações antes de responder se concorda!\nMas obrigatório para quem possui a tag @CTA."
        )

        try:
            # Enviar embed na DM
            dm = await after.create_dm()
            msg = await dm.send(embed=embed)

            # Adicionar reações
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")

            def check(reaction, user):
                return (
                    user == after
                    and str(reaction.emoji) in ["✅", "❌"]
                    and reaction.message.id == msg.id
                )

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=120)  # 2 minutos

                if str(reaction.emoji) == "✅":
                    print(f"{after.display_name} aceitou.")
                    Mongo.register(str(after.id), after.display_name) 
                else:
                    print(f"{after.display_name} recusou.")
                    await after.remove_roles(cta_role, reason="Recusou a CTA")
                    await dm.send("❌ Você recusou a participação no cargo CTA. Seu cargo removido.❌")

            except asyncio.TimeoutError:
                print(f"{after.display_name} não respondeu no tempo.")
                await after.remove_roles(cta_role, reason="Não respondeu à verificação CTA")
                await dm.send("⏰ Tempo expirado! Você não respondeu a tempo. Cargo removido.")

        except Exception as e:
            print(f"❌ Erro ao mandar DM ou processar reações: {e}")


# ------ /// End CTA /// ------ 
@bot.command("end_cta")
@commands.has_role("CTA MANAGER")  # Apenas quem tem o cargo "CTA MANAGER" pode usar
async def sair(ctx):
    try:
        # Pegar o nome do canal de voz salvo no Mongo
        voice_channel_name = Mongo.get_server_properties(str(ctx.guild.id))["voice_channel_name"]

        # Procurar o canal no servidor
        channel = discord.utils.get(ctx.guild.voice_channels, name=voice_channel_name)

        if not channel:
            await ctx.send(f"❌ Canal de voz '{voice_channel_name}' não encontrado.")
            return

        # Retirar todas as pessoas da sala, se houver
        if channel.members:
            for member in list(channel.members):  # Convertendo para lista para segurança
                await member.move_to(None)

        # Trancar a sala (ninguém pode mais conectar)
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False  # Bloqueia a conexão
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send(f"✅ Canal **{channel.name}** esvaziado e trancado com sucesso!")

    except Exception as e:
        await ctx.send(f"❌ Erro ao tentar esvaziar e trancar o canal: {e}")


# ------ /// Open CTA room /// ------
@bot.command("open_cta")
@commands.has_role("CTA MANAGER")
async def open_cta(ctx) : 

    try : 
        # Pegar o nome do canal de voz salvo no Mongo
        voice_channel_name = Mongo.get_server_properties(str(ctx.guild.id))["voice_channel_name"]

        # Procurar o canal no servidor
        channel = discord.utils.get(ctx.guild.voice_channels, name=voice_channel_name)

        if not channel:
            await ctx.send(f"❌ Canal de voz '{voice_channel_name}' não encontrado.")
            return
        
        else : 
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.connect = True  # Bloqueia a conexão
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

            await ctx.send(f"✅ Canal **{channel.name}** liberado com sucesso!")


    except Exception as e : 
        await ctx.send(f"Houve um problema tentando abrir a sala : {e}")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    scheduler.start()  

if __name__ == "__main__" : 
    bot.run(TOKEN)