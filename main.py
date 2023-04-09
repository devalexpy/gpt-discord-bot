from decouple import config
import discord
import openai
import asyncio

openai.api_key = config('OPENAI_API_KEY')
bot = discord.Bot(intents=discord.Intents.all())

conversation_log = [{
    "role": "system",
    "content": "Hello, I'm a chatbot. I'm here to help you with your questions about the OpenAI API. Ask me anything!"
}]


@bot.event
async def on_ready():
    print("I'm ready!")


@bot.slash_command(name="set-channel", description="Chat with the bot")
async def set_channel(ctx, channel: discord.TextChannel):
    global channel_id
    channel_id = channel.id
    await ctx.respond(f"Channel set to {channel.mention}")


@bot.event
async def on_message(ctx):
    if (ctx.channel.id != channel_id):
        return

    if (ctx.author.bot):
        return

    if (ctx.content.startswith("/")):
        return

    conversation_log.append({
        "role": "user",
        "content": ctx.content
    })

    async with ctx.channel.typing():
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=conversation_log,
        )

        text = response["choices"][0]["message"]["content"]

        await asyncio.sleep(1)

        if len(text) > 2000:
            message_parts = [text[i:i+2000]
                             for i in range(0, len(text), 2000)]
            for part in message_parts:
                await ctx.channel.send(part)
        else:
            await ctx.channel.send(text)

    conversation_log.append({
        "role": "system",
        "content": text
    })

    if (len(conversation_log) > 20):
        conversation_log.pop(0)


bot.run(config('BOT_TOKEN'))
