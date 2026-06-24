import discord
import asyncio
import aiohttp
import urllib.parse

# ========== CONFIGURATION ==========
TOKEN = os.getenv("TOKEN")
# ===================================
SUPER_EMOJI = "☠️"
# ===================================

client = discord.Client(self_bot=True)
auto_react_enabled = True  

async def add_super_reaction(channel_id, message_id, emoji):
    """Add a super reaction (burst) to a message."""
    encoded = urllib.parse.quote(emoji)
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{encoded}/@me?burst=true"
    headers = {"Authorization": TOKEN}
    
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers) as resp:
            if resp.status == 204:
                return True
            elif resp.status == 429:
                retry = (await resp.json()).get('retry_after', 1)
                await asyncio.sleep(retry)
                return await add_super_reaction(channel_id, message_id, emoji)
            else:
                print(f" Failed: HTTP {resp.status}")
                return False

@client.event
async def on_ready():
    print(f" Auto-super-react bot logged in as {client.user}")
    print(f" Will add super reaction '{SUPER_EMOJI}' to EVERY message you send")
    print("\nCommands:")
    print("  .autosuper on   - Enable auto super reactions")
    print("  .autosuper off  - Disable auto super reactions")
    print("  .autosuper set 🔥 - Change emoji")
    print("  .autosuper status - Show current status")

@client.event
async def on_message(message):
    global auto_react_enabled, SUPER_EMOJI
    
    # React to your OWN messages
    if message.author == client.user and auto_react_enabled:
        # Small delay to ensure message is fully sent
        await asyncio.sleep(0.2)
        await add_super_reaction(message.channel.id, message.id, SUPER_EMOJI)
        return
    
    # Commands (only respond to your own commands)
    if message.author != client.user:
        return
    
    if not message.content.startswith("."):
        return
    
    parts = message.content.split()
    cmd = parts[0].lower()
    args = parts[1:]
    
    if cmd == ".autosuper" and len(args) >= 1:
        if args[0].lower() == "on":
            auto_react_enabled = True
            await message.channel.send(f" Auto-super react ENABLED | Emoji: {SUPER_EMOJI}")
        elif args[0].lower() == "off":
            auto_react_enabled = False
            await message.channel.send(" Auto-super react DISABLED")
        elif args[0].lower() == "set" and len(args) >= 2:
            SUPER_EMOJI = args[1]
            auto_react_enabled = True
            await message.channel.send(f" Emoji changed to: {SUPER_EMOJI} | Auto-super react ENABLED")
        elif args[0].lower() == "status":
            await message.channel.send(f"Auto-super react: {'ON' if auto_react_enabled else 'OFF'} | Emoji: {SUPER_EMOJI}")
        else:
            await message.channel.send("Usage: .autosuper on/off/set <emoji>/status")
    
    elif cmd == ".testburst":
        # Test command - adds super reaction to a test message
        test_msg = await message.channel.send(" Testing super reaction burst!")
        await add_super_reaction(message.channel.id, test_msg.id, SUPER_EMOJI)

if __name__ == "__main__":
    # Check if token is set
    if TOKEN == "your_discord_token_here":
        print(" Please replace 'your_discord_token_here' with your actual Discord token")
    else:
        client.run(TOKEN)
