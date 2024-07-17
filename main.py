import discord
import settings
import json
import time
from discord.ext import commands, tasks
from mongodb_ah import *
from query_mabi_base import *

logger = settings.logging.getLogger("bot")
collection = get_collection()

###
# Class:       AddItemModal
# Description: Use for ah_add_item command
###

class AddItemModal(discord.ui.Modal, title="Add Item"):
    item_name  = discord.ui.TextInput(label="Item Name", required=True, max_length=100, style=discord.TextStyle.short)
    item_id    = discord.ui.TextInput(label="Item ID", required=True, max_length=100, style=discord.TextStyle.short)
    item_price = discord.ui.TextInput(label="Item Price", required=True, max_length=100, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        current_time = int(time.time())
        response     = query_item_from_mabi_base(self.item_id, current_time)
        total_result = response.json()[0]['data']['auctionHouse']['total']
        item = {
            "name": f"{self.item_name}",
            "id": f"{self.item_id}",
            "price": f"{self.item_price}",
            "last_match": f"{current_time}",
            "total_result": f"{total_result}"
        }
        insert_item(collection, item)
        await interaction.response.send_message(f"Added: {self.item_name} ({self.item_id}) at {self.item_price} by {interaction.user.mention}")
        
    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        logger.error(f"Error in AddItemModal: {error}")


###
# Class:       EditItemModal
# Description: Use for ah_edit_item command.
###

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

###
# Function: discord_run()
# Commands: ah_ping, ah_list, ah_add_item, ah_edit_item, ah_delete_item
###

def discord_run():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    channel = None

    @bot.event
    async def on_ready():
        nonlocal channel
        channel = bot.get_channel(settings.DISCORD_CHANNEL_ID)
        bot.tree.copy_global_to(guild=settings.DISCORD_SERVER_ID)
        await bot.tree.sync(guild=settings.DISCORD_SERVER_ID)
        logger.info(f"User: {bot.user} (ID: {bot.user.id})" )
        if not ah_alert_channel.is_running():
            ah_alert_channel.start()
    
    @bot.command()
    async def ah_ping(ctx):
        """ Answers with pong """
        await ctx.send("pong")
    
    @bot.tree.command()
    async def ah_list(interaction: discord.Interaction):
        ah_list = get_all_items_in_collection(get_collection(), False)
        await interaction.response.send_message("Currently Watching: ```{}```".format(json.dumps(ah_list, indent=2)))

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

    @tasks.loop(seconds=5)
    async def ah_alert_channel():
      item_list = get_all_items_in_collection(collection, True)
      for item in item_list:
          current_time      = int(time.time())
          item_name         = item["name"]
          item_id           = item["id"]
          item_price        = int(item["price"].replace(",", ""))
          item_last_match   = item["last_match"]
          item_total_result = int(item["total_result"])

          response         = query_item_from_mabi_base(item_id, item_last_match)
          new_total_result = response.json()[0]['data']['auctionHouse']['total']

          # If new item was added, then:
          if new_total_result > item_total_result:
              #Get the first result price (query sorted ItemPrice by Ascending)
              first_result = response.json()[0]['data']['auctionHouse']['results'][0]
              lowest_price = int(first_result["price1"])

              #If first result price is lower or equal to watch price, then alert channel
              if lowest_price <= item_price:
                await channel.send(f"{item_name} is at {lowest_price}")

          #Update the last_match time to the current time and new total result
          update_last_match(collection, item_id, current_time, new_total_result)


    bot.run(settings.DISCORD_API_TOKEN, root_logger = True)

if __name__ == "__main__":
    discord_run()