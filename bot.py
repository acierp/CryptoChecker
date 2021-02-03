import discord, asyncio, requests, re, time, os, sys, json;from re import search;from discord.ext import commands;from discord.ext.commands import has_permissions, MissingPermissions
import subprocess
import random
import json
from itertools import cycle

with open('config.json', 'r+', encoding='utf-8') as f:
    config = json.load(f)

bot = commands.Bot(command_prefix='$')

bot.remove_command('help')
@bot.event
async def on_ready():
    os.system('title Bot running.')
    print('Bot started / Running.')
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help | BTC: "))

displayoptions = ["If you'd like to contribute to the bot's development (not required), feel free to send any necessary amount to 17rpaAv4XXDLeTLP6kzMKxd3d3zqdkCpgD", " Invite this discord bot to your server! https://discord.com/oauth2/authorize?client_id=806580500986593282&scope=bot"]
def checkConfirmations(txid, proxy=None):
    if proxy == None:
        getconv = requests.get(f'https://api.blockcypher.com/v1/btc/main/txs/{txid}?limit=50&includeHex=true')
        if getconv.status_code == 200:
            if getconv.json()['double_spend'] == True:
                return "DoubleSpent"
            else:
                return getconv.json()['confirmations']
        else:
            return checkConfirmations(txid)

def blockcypheraccelerate(rawtxid):
    data = {
        'tx': rawtxid
    }
    r = requests.post(' https://api.blockcypher.com/v1/bcy/test/txs/push', data=data)
    if r.status_code == 200:
        return True
    else:
        return False
def smartbitaccelerate(rawtxid):
    data = {
        'hex': rawtxid
    }
    r = requests.post('https://api.smartbit.com.au/v1/blockchain/pushtx', data=data)
    if r.status_code == 200:
        return True
    else:
        return False

def coinbinaccelerate(rawtxid):
    params = {
        'uid': 1,
        'key': 12345678901234567890123456789012,
        'setmodule': 'bitcoin',
        'request': 'sendrawtransaction'
    }
    data = {
        'rawtx': rawtxid
    }
    r = requests.get(f'https://coinb.in/api/?uid=1&key=12345678901234567890123456789012&setmodule=bitcoin&request=sendrawtransaction', params=params, data=data)
    if r.status_code == 200:
        return True
    else:
        return False

@bot.command()
async def check(ctx, txid=None, confcheck=None):
    if txid != None:
        try:
            if confcheck == None:
                confcheck = 1
            
            currrentconf = checkConfirmations(txid)
            if currrentconf != 'DoubleSpent':
                if int(checkConfirmations(txid)) >= int(confcheck):
                    embed = discord.Embed(
                        description=f'{ctx.author.mention}, your transaction ``{txid}`` has already hit ``{confcheck}`` confirmations. The transaction is currently on ``{checkConfirmations(txid)}`` confirmation(s).',
                        color=0xd43b33
                        )

                    embed.set_footer(text=random.choice(displayoptions))

                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f'{ctx.author.mention}, monitoring your transaction ``{txid}`` on the bitcoin network for ``{confcheck}`` confirmations. The transaction is currently on ``{checkConfirmations(txid)}`` confirmations.',
                        color=0x5CDBF0
                        )

                    embed.set_footer(text=random.choice(displayoptions))

                    message = await ctx.send(embed=embed)

                    embed = discord.Embed(
                        description=f'{ctx.author.mention}, monitoring your transaction ``{txid}`` on the bitcoin network for ``{confcheck}`` confirmations. The transaction is currently on ``{checkConfirmations(txid)}`` confirmations.\n**Your transaction was successfully accelerated on smartbit, coinbin, and blockcypher!** ✅',
                        color=0x38f232
                        )

                    embed.set_footer(text=random.choice(displayoptions))


                    boosttxid = requests.get(f'https://blockstream.info/api/tx/{txid}/hex').text
                    coinbinaccelerate(boosttxid)
                    smartbitaccelerate(boosttxid)
                    blockcypheraccelerate(boosttxid)
                    await message.edit(embed=embed)
                    while True:
                        await asyncio.sleep(30)
                        currrentconf = checkConfirmations(txid)
                        if currrentconf != 'DoubleSpent':
                            if int(currrentconf) >= int(confcheck):
                                await ctx.send(f'{ctx.author.mention}, your transaction ``{txid}`` has successfully hit ``{confcheck}`` confirmations.')
                                await ctx.author.send(f'{ctx.author.mention}, your transaction ``{txid}`` has successfully hit ``{confcheck}`` confirmations.')
                                break
                        else:
                            embed = discord.Embed(
                                description=f'{ctx.author.mention} **WARNING** your transaction ``{txid}`` was maliciously labeled as doublespent on the senders\' side. If you are undergoing a deal, please stay cautious and know that the bitcoin delivered will be rolled back to the sender.',
                                color=0xd43b33
                                )

                            embed.set_footer(text=random.choice(displayoptions))

                            message = await ctx.send(embed=embed)
                            message = await ctx.author.send(embed=embed)
            else:
                embed = discord.Embed(
                description=f'{ctx.author.mention} **WARNING** your transaction ``{txid}`` was maliciously labeled as doublespent on the senders\' side. If you are undergoing a deal, please stay cautious and know that the bitcoin delivered will be rolled back to the sender.',
                color=0xd43b33
                )

                embed.set_footer(text=random.choice(displayoptions))

                message = await ctx.send(embed=embed)
                await ctx.author.send(embed=embed)

        except discord.ext.commands.errors.MissingRequiredArgument:
            await ctx.send(f'{ctx.author.mention}, a required arguement is missing when using this command. Please retry the command by running ``!check (txid) (confirmations)``')
    else: 
        await ctx.author.send('The required bitcoin network transaction ID is missing when using this command. Please retry the command by running ``!check (txid) (confirmations)``')

@bot.command()
async def invite(ctx):
    await ctx.send(f'{ctx.author.mention}, invite the ``Crypto Checker`` discord bot to your discord server by using the following link: https://discord.com/oauth2/authorize?client_id=806580500986593282&scope=bot')

@bot.command()
async def help(ctx):
    pass

bot.run(config['token'])
