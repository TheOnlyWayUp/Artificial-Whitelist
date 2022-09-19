import disnake
from disnake.ext import commands, tasks
from config import BOT_CONFIG, get_data, set_data
from typing import cast

bot = commands.InteractionBot(test_guilds=BOT_CONFIG["guilds"])

# --- #


@bot.slash_command_check
async def moderator_check(interaction: disnake.ApplicationCommandInteraction):
    roles = [role.id for role in cast(disnake.Member, interaction.author).roles]

    allowed = False
    for moderator_role_id in BOT_CONFIG["moderator_roles"]:
        if moderator_role_id in roles:
            allowed = True
            break
    if not allowed:
        # raise FailedModeratorCheck(interaction) | Spent a while going through different ways to catch this error, decided to just handle it here
        await interaction.send(
            embed=disnake.Embed(
                title="You're not allowed to use this command.",
                color=disnake.Color.dark_red(),
            ),
            ephemeral=True,
        )
        return False
    return True


@bot.slash_command(
    name="config",
    description="View and Modify configuration settings for the Proxy.",
    dm_permission=False,
)
async def config_group(
    interaction: disnake.ApplicationCommandInteraction,
):
    ...


# --- Player Config Commands --- #


@config_group.sub_command_group(
    name="player", description="Player Configuration Commands."
)
async def player_config_group(
    interaction: disnake.ApplicationCommandInteraction,
):
    ...


@player_config_group.sub_command(
    name="add",
    description="Add a player to the playerlist. Behaviour changes based on ProxyMode.",
)
async def add_player_to_playerlist(
    interaction: disnake.ApplicationCommandInteraction,
    username: str = commands.Param(
        description="Username of the Player", min_length=3, max_length=16
    ),
):
    username = username.lower()

    data = get_data()
    data["players"].append(username)
    PLAYER_LIST.append(username)
    set_data(**data)

    return await interaction.send(
        embed=disnake.Embed(
            title="Updated",
            description="Players on the list are -\n{}".format(
                ", ".join(data["players"])
            ),
            color=disnake.Color.dark_green(),
        ).set_footer(text="Proxy Mode - {}".format(data["mode"])),
        ephemeral=True,
    )


PLAYER_LIST = get_data()["players"]


async def autocomplete_playerlist(
    interaction: disnake.ApplicationCommandInteraction, string: str
):
    roles = [role.id for role in cast(disnake.Member, interaction.author).roles]

    allowed = False
    for moderator_role_id in BOT_CONFIG["moderator_roles"]:
        if moderator_role_id in roles:
            allowed = True
            break
    if not allowed:
        return ["403"]

    return [player for player in PLAYER_LIST if string.lower() in player.lower()]


@player_config_group.sub_command(
    name="remove",
    description="Remove a player from the playerlist. Behaviour changes based on ProxyMode.",
)
async def remove_player_from_playerlist(
    interaction: disnake.ApplicationCommandInteraction,
    username: str = commands.Param(
        description="Username of the Player",
        min_length=3,
        max_length=16,
        autocomplete=autocomplete_playerlist,
    ),
):

    data = get_data()
    try:
        data["players"].remove(username)
        PLAYER_LIST.remove(username)
    except:
        ...
    set_data(**data)

    return await interaction.send(
        embed=disnake.Embed(
            title="Updated",
            description="Players on the list are -\n{}".format(
                ", ".join(data["players"])
            ),
            color=disnake.Color.dark_green(),
        ).set_footer(text="Proxy Mode - {}".format(data["mode"])),
        ephemeral=True,
    )


@player_config_group.sub_command(name="view", description="View players on the list.")
async def view_playerlist(interaction: disnake.ApplicationCommandInteraction):

    data = get_data()

    return await interaction.send(
        embed=disnake.Embed(
            title="Player List",
            description="Players on the list are -\n{}".format(
                ", ".join(data["players"])
            ),
            color=disnake.Color.og_blurple(),
        ).set_footer(text="Proxy Mode - {}".format(data["mode"])),
        ephemeral=True,
    )


# --- Proxy Mode Config --- #


@config_group.sub_command_group(
    name="mode", description="Proxy Mode Configuration Commands."
)
async def mode_config_group(
    interaction: disnake.ApplicationCommandInteraction,
):
    ...


@mode_config_group.sub_command(name="view", description="View Proxy Mode.")
async def view_proxy_mode(interaction: disnake.ApplicationCommandInteraction):

    data = get_data()

    return await interaction.send(
        embed=disnake.Embed(
            title="Proxy Mode",
            description="The Proxy Mode is - `{}`".format(data["mode"]),
            color=disnake.Color.blurple(),
        ).add_field(name="Players", value=", ".join(data["players"])),
        ephemeral=True,
    )


PROXY_MODE_OPTIONS = ["whitelist", "blacklist"]


async def autocomplete_proxy_mode(inter, string: str):
    return [
        proxy_mode
        for proxy_mode in PROXY_MODE_OPTIONS
        if string.lower() in proxy_mode.lower()
    ]


@mode_config_group.sub_command(
    name="change",
    description="Add a player to the playerlist. Behaviour changes based on ProxyMode.",
)
async def change_proxy_mode(
    interaction: disnake.ApplicationCommandInteraction,
    mode: str = commands.Param(autocomplete=autocomplete_proxy_mode),
):

    data = get_data()
    old_mode = data["mode"]
    data["mode"] = mode
    set_data(**data)

    return await interaction.send(
        embed=disnake.Embed(
            title="Updated",
            description="`{}` -> `{}`".format(old_mode, mode),
            color=disnake.Color.dark_green(),
        ).add_field(name="Players", value=", ".join(data["players"])),
        ephemeral=True,
    )


# --- #


@tasks.loop(seconds=30)
async def update_cached_playerlist():
    global PLAYER_LIST
    PLAYER_LIST = get_data()["players"]


# --- #


@bot.event
async def on_ready():
    print(
        "Logged in as {} and in {} guild{}.".format(
            bot.user, len(bot.guilds), "" if len(bot.guilds) == 1 else "s"
        )
    )
    update_cached_playerlist.start()


# --- #

if __name__ == "__main__":
    bot.run(BOT_CONFIG["token"])
