import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime
from data_manager import DataManager
from config import Config

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
data_manager = DataManager()

class PurchaseApprovalView(discord.ui.View):
    def __init__(self, user_id, item_name, item_cost, balance_before, balance_after):
        super().__init__(timeout=300)  # 5 minute timeout
        self.user_id = user_id
        self.item_name = item_name
        self.item_cost = item_cost
        self.balance_before = balance_before
        self.balance_after = balance_after
    
    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green, emoji='✅')
    async def accept_purchase(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has approval permissions
        if not any(role.name.lower() in Config.STAFF_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to approve purchases.", ephemeral=True)
            return
        
        try:
            # Get the user who made the purchase
            user = bot.get_user(self.user_id)
            if user is None:
                await interaction.response.send_message("Could not find the user who made this purchase.", ephemeral=True)
                return
            
            # Remove from pending purchases
            data_manager.remove_pending_purchase(self.user_id, self.item_name)
            
            # Send DM to user
            try:
                await user.send(f"✅ **Purchase Approved!**\n\nSuccessfully bought **{self.item_name}**.\nGive the staff a few hours to give you the **{self.item_name}** in game.")
            except discord.Forbidden:
                # If DM fails, try to send in the channel
                await interaction.followup.send(f"✅ Purchase approved for {user.mention}! Could not send DM, so notifying here: Successfully bought **{self.item_name}**. Give the staff a few hours to give you the item in game.")
            
            # Update the embed to show it's been approved
            embed = discord.Embed(
                title="✅ Purchase Approved",
                description=f"**{user.display_name}** bought **{self.item_name}** for **{self.item_cost} points**.\n\n**Previous balance:** {self.balance_before} points\n**Current balance:** {self.balance_after} points\n\n**Approved by:** {interaction.user.display_name}",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Disable the button
            for item in self.children:
                item.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)
            
            # Log the approval
            print(f"Purchase approved: {user.display_name} bought {self.item_name} for {self.item_cost} points (approved by {interaction.user.display_name})")
            
        except Exception as e:
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(f"An error occurred while processing the approval: {str(e)}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"An error occurred while processing the approval: {str(e)}", ephemeral=True)
            except:
                print(f"Failed to send error message: {str(e)}")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready and serving {len(bot.guilds)} guilds.')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="givepoints", description="Give points to a user (Staff only)")
async def give_points(interaction: discord.Interaction, user: discord.Member, amount: int):
    # Check if user has staff permissions
    if not any(role.name.lower() in Config.STAFF_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to give points. Only staff members can use this command.", ephemeral=True)
        return
    
    if amount <= 0:
        await interaction.response.send_message("❌ Amount must be greater than 0.", ephemeral=True)
        return
    
    # Add points to user
    new_balance = data_manager.add_points(user.id, amount)
    
    embed = discord.Embed(
        title="💰 Points Awarded",
        description=f"Successfully gave **{amount} points** to {user.display_name}!\n\n**New balance:** {new_balance} points",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Awarded by {interaction.user.display_name}")
    
    await interaction.response.send_message(embed=embed)
    
    # Log the transaction
    print(f"Points awarded: {interaction.user.display_name} gave {amount} points to {user.display_name}")

@bot.tree.command(name="balance", description="Check your point balance")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target_user = user if user else interaction.user
    balance = data_manager.get_balance(target_user.id)
    
    embed = discord.Embed(
        title="💰 Point Balance",
        description=f"**{target_user.display_name}** has **{balance} points**",
        color=0x3498db,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stock", description="View available items for purchase")
async def stock(interaction: discord.Interaction):
    stock_items = data_manager.get_stock()
    
    if not stock_items:
        embed = discord.Embed(
            title="🏪 Shop Stock",
            description="No items available for purchase at the moment.",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(
        title="🏪 Shop Stock",
        description="Available items for purchase:",
        color=0x9b59b6,
        timestamp=datetime.now()
    )
    
    for item_name, item_data in stock_items.items():
        embed.add_field(
            name=f"💎 {item_name}",
            value=f"**Price:** {item_data['cost']} points\n**Description:** {item_data.get('description', 'No description available')}",
            inline=False
        )
    
    embed.set_footer(text="Use /buy <item_name> to purchase an item")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="buy", description="Purchase an item from the shop")
async def buy(interaction: discord.Interaction, item_name: str):
    stock_items = data_manager.get_stock()
    user_balance = data_manager.get_balance(interaction.user.id)
    
    # Find the item (case-insensitive)
    item_key = None
    for key in stock_items.keys():
        if key.lower() == item_name.lower():
            item_key = key
            break
    
    if not item_key:
        embed = discord.Embed(
            title="❌ Item Not Found",
            description=f"Item '**{item_name}**' not found in stock.\n\nUse `/stock` to see available items.",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    item_data = stock_items[item_key]
    item_cost = item_data['cost']
    
    # Check if user has enough points
    if user_balance < item_cost:
        embed = discord.Embed(
            title="❌ Insufficient Points",
            description=f"You need **{item_cost} points** to buy **{item_key}**.\n\n**Your balance:** {user_balance} points\n**Needed:** {item_cost - user_balance} more points",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Deduct points temporarily and add to pending
    balance_before = user_balance
    balance_after = data_manager.deduct_points(interaction.user.id, item_cost)
    data_manager.add_pending_purchase(interaction.user.id, item_key, item_cost)
    
    # Send success message to user
    embed = discord.Embed(
        title="✅ Purchase Initiated",
        description=f"Successfully purchased **{item_key}** for **{item_cost} points**!\n\n**Previous balance:** {balance_before} points\n**Current balance:** {balance_after} points\n\nYour purchase is now pending approval.",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Send approval request to designated channel
    approval_channel_id = Config.APPROVAL_CHANNEL_ID
    approval_channel = bot.get_channel(approval_channel_id)
    
    if approval_channel:
        # Ping the approval role
        approval_role_id = Config.APPROVAL_ROLE_ID
        approval_ping = f"<@&{approval_role_id}>" if approval_role_id else "@here"
        
        approval_embed = discord.Embed(
            title="🛒 Purchase Approval Required",
            description=f"**{interaction.user.display_name}** bought **{item_key}** for **{item_cost} points**.\n\n**User's balance was:** {balance_before} points\n**Current balance:** {balance_after} points",
            color=0xffa500,
            timestamp=datetime.now()
        )
        approval_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        approval_embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        view = PurchaseApprovalView(interaction.user.id, item_key, item_cost, balance_before, balance_after)
        
        await approval_channel.send(
            content=f"{approval_ping}",
            embed=approval_embed,
            view=view
        )
    else:
        print(f"Warning: Approval channel {approval_channel_id} not found!")

@bot.tree.command(name="addstock", description="Add an item to the shop (Staff only)")
async def add_stock(interaction: discord.Interaction, item_name: str, cost: int, description: str = ""):
    # Check if user has staff permissions
    if not any(role.name.lower() in Config.STAFF_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to manage stock. Only staff members can use this command.", ephemeral=True)
        return
    
    if cost <= 0:
        await interaction.response.send_message("❌ Item cost must be greater than 0.", ephemeral=True)
        return
    
    # Add item to stock
    data_manager.add_stock_item(item_name, cost, description)
    
    embed = discord.Embed(
        title="✅ Stock Item Added",
        description=f"Successfully added **{item_name}** to the shop!\n\n**Price:** {cost} points\n**Description:** {description if description else 'No description provided'}",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Added by {interaction.user.display_name}")
    
    await interaction.response.send_message(embed=embed)
    print(f"Stock item added: {interaction.user.display_name} added '{item_name}' for {cost} points")

@bot.tree.command(name="removestock", description="Remove an item from the shop (Staff only)")
async def remove_stock(interaction: discord.Interaction, item_name: str):
    # Check if user has staff permissions
    if not any(role.name.lower() in Config.STAFF_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to manage stock. Only staff members can use this command.", ephemeral=True)
        return
    
    # Check if item exists
    stock_items = data_manager.get_stock()
    item_key = None
    for key in stock_items.keys():
        if key.lower() == item_name.lower():
            item_key = key
            break
    
    if not item_key:
        await interaction.response.send_message(f"❌ Item '**{item_name}**' not found in stock.", ephemeral=True)
        return
    
    # Remove item from stock
    data_manager.remove_stock_item(item_key)
    
    embed = discord.Embed(
        title="✅ Stock Item Removed",
        description=f"Successfully removed **{item_key}** from the shop!",
        color=0xff6b6b,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Removed by {interaction.user.display_name}")
    
    await interaction.response.send_message(embed=embed)
    print(f"Stock item removed: {interaction.user.display_name} removed '{item_key}'")

@bot.tree.command(name="setbalance", description="Set a user's point balance (Staff only)")
async def set_balance(interaction: discord.Interaction, user: discord.Member, amount: int):
    # Check if user has staff permissions
    if not any(role.name.lower() in Config.STAFF_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to set balances. Only staff members can use this command.", ephemeral=True)
        return
    
    if amount < 0:
        await interaction.response.send_message("❌ Balance cannot be negative.", ephemeral=True)
        return
    
    # Set user balance
    old_balance = data_manager.get_balance(user.id)
    data_manager.set_balance(user.id, amount)
    
    embed = discord.Embed(
        title="💰 Balance Updated",
        description=f"Successfully set **{user.display_name}**'s balance!\n\n**Previous balance:** {old_balance} points\n**New balance:** {amount} points",
        color=0xffa500,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Updated by {interaction.user.display_name}")
    
    await interaction.response.send_message(embed=embed)
    print(f"Balance set: {interaction.user.display_name} set {user.display_name}'s balance to {amount} points")

@bot.tree.command(name="help", description="Show bot commands and usage")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Here are all available commands:",
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="👥 User Commands",
        value="`/balance` - Check your point balance\n`/balance @user` - Check another user's balance\n`/stock` - View available items\n`/buy <item>` - Purchase an item",
        inline=False
    )
    
    # Check if user has staff permissions to show admin commands
    if any(role.name.lower() in Config.STAFF_ROLES for role in interaction.user.roles):
        embed.add_field(
            name="🔧 Staff Commands",
            value="`/givepoints @user <amount>` - Give points to a user\n`/setbalance @user <amount>` - Set a user's balance\n`/addstock <name> <cost> [description]` - Add item to shop\n`/removestock <name>` - Remove item from shop",
            inline=False
        )
    
    embed.add_field(
        name="💡 How it works",
        value="1. Staff give you points using `/givepoints`\n2. Check available items with `/stock`\n3. Buy items with `/buy` - your purchase needs approval\n4. Staff will approve and give you the item in-game",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    embed = discord.Embed(
        title="❌ Error",
        description=f"An error occurred: {str(error)}",
        color=0xe74c3c
    )
    await ctx.send(embed=embed)

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error):
    embed = discord.Embed(
        title="❌ Error",
        description=f"An error occurred: {str(error)}",
        color=0xe74c3c
    )
    
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
        exit(1)
    
    bot.run(token)
