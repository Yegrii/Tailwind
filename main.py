import discord
import random
import requests
import json
from discord.ext import commands
from bot_token import disc_token, weather_token


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

# Token and URL for the bot
# Discord token
my_secret = disc_token
# Weather API token
weather_api_key = weather_token
# Path to m3u file with radio links
m3u_file_path = "KissFM.m3u"


def get_quote():
    # Get random quote from zenquotes.io
    response = requests.get('https://zenquotes.io/api/random')
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + ' - ' + json_data[0]['a']
    return quote


def save_request(username, request, response):
    # Save request to file
    with open('your_file_name.txt', 'a') as file:
        file.write(f'Username: {username}\n')
        file.write(f'Request: {request}\n')
        file.write(f'Response: {response}\n')
        file.write('---\n')


@bot.event
async def on_ready():
    # Print bot name in console when bot is ready
    print('We have logged in as {0}'.format(bot.user))
    

@bot.event
async def on_member_join(member):
    # Send message to system channel when user join server
    channel = member.guild.system_channel
    if channel is not None:
        quote = get_quote()
        await channel.send(f'{member.mention}! Hello and welcome to the server!')
        await channel.send(quote)
        save_request(member.name, 'join', quote)


@bot.command()
async def sad(ctx):
    # Send random quote from zenquotes.io
    quote = get_quote()
    await ctx.send(quote)
    save_request(ctx.author.name, 'sad', quote)


@bot.command()
async def coin(ctx):
    # Flip a coin
    sides = ['Heads', 'Tails']
    result = random.choice(sides)
    await ctx.send(f'Result: {result}')


@bot.command()
async def bitcoin(ctx):
    # Get bitcoin price from coingecko.com
    response = requests.get('https://api.coingecko.com/api/v3/coins/bitcoin')
    data = response.json()
    name = data['name']
    symbol = data['symbol']
    price = data['market_data']['current_price']['usd']
    price_change = data['market_data']['price_change_24h']
    market_cap = data['market_data']['market_cap']['usd']

    price_change_sign = "+" if price_change > 0 else "-"
    price_change = round(abs(price_change), 2)

    info_message = f'{name} ({symbol}):\nPrice: ${price}\nPrice Change (24h): {price_change_sign}${price_change}\n ' \
                   f'Market Cap: ${market_cap}'
    await ctx.send(info_message)
    save_request(ctx.author.name, 'bitcoin', info_message)


@bot.command()
async def dogcoin(ctx):
    # Get dogecoin price from coingecko.com
    response = requests.get('https://api.coingecko.com/api/v3/coins/dogecoin')
    data = response.json()
    name = data['name']
    symbol = data['symbol']
    price = data['market_data']['current_price']['usd']
    price_change = data['market_data']['price_change_24h']
    market_cap = data['market_data']['market_cap']['usd']

    price_change_sign = "+" if price_change > 0 else "-"
    price_change = round(abs(price_change), 5)

    info_message = f'{name} ({symbol}):\nPrice: ${round(price, 3)}\nPrice Change (24h): {price_change_sign}' \
                   f'${price_change}\n Market Cap: ${market_cap}'
    await ctx.send(info_message)


@bot.command()
async def weather(ctx, city):
    # Get weather info from weatherapi.com
    url = f'http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=ru'
    response = requests.get(url)
    data = response.json()

    if 'error' not in data:
        city_name = data['location']['name']
        temperature = data['current']['temp_c']
        weather_desc = data['current']['condition']['text']

        weather_message = f'Weather in town {city_name}:\nTemperature: {temperature}°C\nDescription: {weather_desc}'
        await ctx.send(weather_message)
        save_request(ctx.author.name, f'weather ({city})', weather_message)
    else:
        await ctx.send('City not found.')


@bot.command()
async def play_radio(ctx):
    # Play radio in voice channel
    voice_channel = ctx.author.voice.channel
    if voice_channel:
        try:
            voice_client = await voice_channel.connect()
            url = "http://online.kissfm.ua/KissFM" # Kiss FM radio
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))
            voice_client.play(source)
            await ctx.send("Launching Kiss FM radio...")
        except discord.ClientException as e:
            await ctx.send("Error: " + str(e))
    else:
        await ctx.send("You should be in voice channel to use this command.")


@bot.command()
async def stop_radio(ctx):
    # Stop playing radio
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Radio stopped.")
    else:
        await ctx.send("Bot is not connected to voice channel.")


@bot.command()
async def volume(ctx, adjustment: str):
    # Change radio volume
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        current_volume = voice_client.source.volume
        if adjustment == "+":
            new_volume = min(current_volume + 0.1, 1.0)
        elif adjustment == "-":
            new_volume = max(current_volume - 0.1, 0.0)
        else:
            await ctx.send("‘+’ or ‘-’ expected")
            return
        voice_client.source.volume = new_volume
        await ctx.send(f"Volume changed from {current_volume} to {new_volume}")
    else:
        await ctx.send("Bot is not connected to voice channel or is not playing anything.")


@bot.command()
async def commands(ctx):
    # Show bot commands
    embed = discord.Embed(title="Bot Commands", description="List of all bot commands", color=0xeee657)
    embed.add_field(name="$sad", value="Send random message", inline=False)
    embed.add_field(name="$bitcoin", value="Information about bitcoin", inline=False)
    embed.add_field(name="$weather <city>", value="Information about weather in city", inline=False)
    embed.add_field(name="$coin", value="Flip the coin", inline=False)
    embed.add_field(name="$dogcoin", value="Information about dogecoin", inline=False)
    embed.add_field(name="$play_radio", value="Play radio", inline=False)
    embed.add_field(name="$stop_radio", value="Stop playing radio", inline=False)
    embed.add_field(name="$volume <+/->", value="Increase or decrease radio volume", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def switch_off_bot(ctx):
    # Switch off bot
    await ctx.send("Bot is switching off...")
    await bot.close()

bot.run(my_secret)
