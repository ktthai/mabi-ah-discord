import discord
import settings
import json
from discord.ext import commands
from mongodb_ah import *

logger = settings.logging.getLogger("bot")
collection = get_collection()

class AddItemModal(discord.ui.Modal, title="Add Item"):
    item_name  = discord.ui.TextInput(label="Item Name", required=True, max_length=100, style=discord.TextStyle.short)
    item_id    = discord.ui.TextInput(label="Item ID", required=True, max_length=100, style=discord.TextStyle.short)
    item_price = discord.ui.TextInput(label="Item Price", required=True, max_length=100, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        item = {
            "name": f"{self.item_name}",
            "id": f"{self.item_id}",
            "price": f"{self.item_price}"
        }
        insert_item(collection, item)
        await interaction.response.send_message(f"Added: {self.item_name} ({self.item_id} at {self.item_price} by {interaction.user.mention}")
        
    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        logger.error(f"Error in AddItemModal: {error}")

class EditItemModal(discord.ui.Modal):
    def __init__(self, item_name, item_id, item_price):
        super().__init__(title=f"Editing Item ID: {item_id}")
        self.original_item_name_value = item_name
        self.item_id_value = item_id
        self.original_item_price_value = item_price

        self.new_item_name = discord.ui.TextInput(
            label="Item Name",
            default=item_name,
            required=False,
            max_length=100,
            style=discord.TextStyle.short
        )
        self.new_item_price = discord.ui.TextInput(
            label="Item Price",
            default=item_price,
            required=True,
            max_length=100,
            style=discord.TextStyle.short
        )

        self.add_item(self.new_item_name)
        self.add_item(self.new_item_price)

    async def on_submit(self, interaction: discord.Interaction):
        original_item_name_value  = self.original_item_name_value
        original_item_price_value = self.original_item_price_value
        new_item_name_value       = self.item_name_input.value
        new_item_price_value      = self.item_price_input.value
        item_id_value             = self.item_id_value

        update_item(collection, item_id_value, new_item_name_value, new_item_price_value)

        await interaction.response.send_message(f"Edited: {original_item_name_value}->{new_item_name_value} (ID: {item_id_value}) from {original_item_price_value}->{new_item_price_value} by {interaction.user.mention}")
        
    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        logger.error(f"Error in EditItemModal: {error}")


def discord_run():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        bot.tree.copy_global_to(guild=settings.DISCORD_SERVER_ID)
        await bot.tree.sync(guild=settings.DISCORD_SERVER_ID)
        logger.info(f"User: {bot.user} (ID: {bot.user.id})" )
    
    @bot.command()
    async def ah_ping(ctx):
        """ Answers with pong """
        await ctx.send("pong")
    
    @bot.tree.command()
    async def ah_list(interaction: discord.Interaction):
        itemList = get_all_items_in_collection(get_collection())
        await interaction.response.send_message("Currently Watching: ```{}```".format(json.dumps(itemList, indent=2)))

    @bot.tree.command()
    async def ah_add_item(interaction: discord.Interaction):
        await interaction.response.send_modal(AddItemModal())

    @bot.tree.command()
    async def ah_edit_item(interaction: discord.Interaction, item_id: int):
        item = find_item_by_id(item_id, collection)
        await interaction.response.send_modal(EditItemModal(item['name'], item['id'], item['price']))

    @bot.tree.command()
    async def ah_delete_item(interaction: discord.Interaction, item_id: int):
        item = find_item_by_id(item_id, collection)
        delete_item(collection, item_id)
        await interaction.response.send_message(f"Delete Item: {item['name']} ({item_id}) by {interaction.user.mention}")

    bot.run(settings.DISCORD_API_TOKEN, root_logger = True)