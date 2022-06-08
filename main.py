import traceback
from os import getenv

from discord import (
    ApplicationContext,
    Option,
    Intents,
    Thread,
    default_permissions,
    Embed
)
from discord.ext.commands import (
    Bot,
    Context,
    bot_has_guild_permissions
)
from dotenv import load_dotenv

load_dotenv()
print([pf for pf in getenv("COMMAND_PREFIX").split(",")])

bot = Bot(
    help_command=None,
    command_prefix=[pf for pf in getenv("COMMAND_PREFIX")],
    intents=Intents.all()
)

gid: str

guild_ids = [(int(gid) if gid.isdigit() else None) for gid in (getenv("GUILD_IDS").split(","))]


@bot.event
async def on_ready():
    print("Logged in as {} : {}".format(bot.user.id, bot.user.name))


positive_emoji: str = "\U00002705"
negative_emoji: str = "\U0000274e"


@bot.slash_command(guild_ids=guild_ids, description="Archive thread.")
async def archive(ctx: ApplicationContext):
    if not isinstance(ctx.channel, Thread):
        return await ctx.respond(
            "here is not Thread"
        )
    await ctx.respond("archived")
    await ctx.channel.archive()
    await ctx.guild.get_channel(
        ctx.channel.parent_id
    ).get_partial_message(
        ctx.channel.id
    ).add_reaction(
        positive_emoji
    )


@bot.slash_command(guild_ids=guild_ids, description="Change thread title.")
@bot_has_guild_permissions(manage_threads=True)
async def set_title(
        ctx: ApplicationContext,
        new_title: Option(str, description="New thread title")
):
    old_title = ctx.channel.name
    if not isinstance(ctx.channel, Thread):
        msg = await ctx.respond(
            "**Here is not Thread. You must try again in ThreadChannel.**\n"
            "This message will delete 3 sec...",
            ephemeral=True
        )
        return await msg.delete(delay=3)

    await ctx.channel.edit(name=new_title)
    await ctx.respond(
        f"changed thread name from {old_title} -> {new_title}"
    )


@bot.slash_command(guild_ids=guild_ids)
@default_permissions(administrator=True)
async def threads(ctx: ApplicationContext):
    threads = ctx.channel.threads
    tstring = "\n".join([f"**{t.name}**" for t in threads])
    await ctx.respond(tstring)


@bot.command(name="archive", aliases=["arc"])
@bot_has_guild_permissions(manage_threads=True)
async def arcive_on_command(
        ctx: Context
) -> None:
    if not isinstance(ctx.channel, Thread):
        msg = await ctx.send(
            "**Here is not Thread. You must try again in ThreadChannel.**\n"
            "This message will delete 3 sec..."
        )
        await ctx.message.delete(delay=3)
        return await msg.delete(delay=3)

    ch: Thread = ctx.channel
    ltst = await ctx.send("archiving...")
    try:
        await ctx.message.add_reaction(positive_emoji)
        await ctx.guild.get_channel(
            ctx.channel.parent_id
        ).get_partial_message(
            ctx.channel.id
        ).add_reaction(
            emoji=positive_emoji
        )
        await ltst.delete()
        await ch.archive()

    except Exception as p:
        await ctx.send(
            "error(s) happened.\n"
            f"{traceback.TracebackException.from_exception(p)}"
        )
        await ctx.message.add_reaction(
            emoji=negative_emoji
        )


@bot.group(name="set", invoke_without_command=True)
async def set_on_command(ctx: Context, *, sub):
    if sub is None:
        return await ctx.send(
            "Usage...\n"
            f"{bot.command_prefix}set <sub_command (required)>\n\n"
            f"```md\n"
            f"# sub command: \n"
            f"- title <new title (required)>\n"
            f"```"
        )


@set_on_command.command(name="title")
async def edit_title_sub(ctx: Context, *, args: str):
    if not isinstance(ctx.channel, Thread):
        return await ctx.send("This is not Thread")
    await ctx.channel.edit(name=args)
    await ctx.send("edited")


@bot.command(name="help")
async def help_on_command(ctx: Context):
    embed = Embed(
        title="help",
        description=f"- **Prefix commands**\n\n"
                    f"{bot.command_prefix}help  -> show this embed.\n"
                    f"{bot.command_prefix}archive  -> thread archive. (you can play this command **only Thread**)\n"
                    f"{bot.command_prefix}set title `<NEW_THREAD_TITLE> (required)` -> thread name change to `NEW_THREAD_TITLE`\n\n\n"
                    f"- **Shash commands**\n\n"
                    f"/archive -> thread archive.\n"
                    f"/set title `<NEW_THREAD_TITLE> (required)"
    )


bot.run(getenv("TOKEN"))
