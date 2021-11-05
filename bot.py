from discord.ext import commands
from dotenv import load_dotenv
from discord.utils import get
import requests
import asyncio
import discord
import random
import pprint
import utils
import json
import time
import os


if not os.path.isfile('.env'):
	print('[!!] Missing .env file')
	exit()
load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
ABUSE = os.getenv('ABUSE')
SERVE = os.getenv('HONEY')
HOSTN = os.getenv('HOSTN')
ARMED = True; TRIGGER = 0
# Load client and Set command prefix
bot = commands.Bot(command_prefix = "$")


def isPotActive():
	c = f'ping -c 1 {SERVE}; echo $?'
	return int(utils.cmd(c,False).pop()) == 0


@bot.event
async def on_ready():
	guild = get(bot.guilds, name=GUILD)
	print(guild)
	print(f'{bot.user} has connected to Discord!')		
	print(f'{guild.name}(id: {guild.id})')
	if isPotActive():
		print('[+] Remote Server is \033[1m\033[34mONLINE\033[0m')
	else:
		print('[+] Remote Server is \033[1m\033[31mOFFLINE\033[0m')


@bot.command(name='report', pass_context=True)
async def report_abuse(ctx, ip, comment, categories):
	# Defining the api-endpoint
	url = 'https://api.abuseipdb.com/api/v2/report'

	# String holding parameters to pass in json format
	params = {
	    'ip':'%s' % ip,
	    'categories':categories,
	    'comment': comment
	}

	headers = {
	    'Accept': 'application/json',
	    'Key': '%s' % ABUSE
	}
	
	response = utils.cmd(cmd,True)
	await ctx.send(json.dumps(params))
	response = requests.request(method='POST', url=url, headers=headers, params=params)
	print(headers)
	# # Formatted output
	await ctx.send('```json\n'+json.dumps(json.loads(response.text))+'\n```')


async def check_alarm(ctx,filename,n):
	print('[-] Checking Alarm File')
	while ARMED:
			await asyncio.sleep(35)
			try:
				c = f"sftp {HOSTN}@{SERVE}:/home/{HOSTN}/TripWire/tripwire/.alerts/alarm/ <<< $'get alarm'"
				utils.arr2str(utils.cmd(c,False))
				if filename in utils.swap(filename, True):
					n = N
					m = '{0.author.mention} **New Connection **'.format(ctx.message)
					m += '```' + utils.arr2str(utils.cmd(f"tail -n 3 {filename} ",False))+'```'
					await ctx.send(m)
					
			except IndexError:
				print('[!] Unable to read log file')
				pass

@bot.command(name='sh', pass_context=True)
async def shell(ctx, *arg):
	c = ' '.join(arg[:])
	fn = utils.execute(c)
	try:
		result = ''
		f = open(fn, 'r')
		while True:
			piece = f.read(1024)  
			if not piece:
				break
			try:
				await ctx.send('```\n'+piece+'\n```')
				time.sleep(1)
			except:
				print(result)
				pass
		f.close()
		os.remove(filename)
		await ctx.send("```"+result+"```")
	except:
		pass


@bot.command(name='kill-honey', pass_context=True)
async def kill_process(ctx):
	c = "ssh %s@%s ps aux | grep serve.py | cut -d ' ' -f 7 | while read n; do kill -9 $n; done"
	utils.cmd(c%(HOSTN,SERVE),False)
	await ctx.send('Honeypot **Killed**')

@bot.command(name='get-pcap', pass_context=True)
async def pull_pcap(ctx):
	c = f"sftp {HOSTN}@{SERVE}:/home/{HOSTN}/ <<< $'get honey.pcap'"
	reply = utils.arr2str(utils.cmd(c,False))
	await ctx.send("'''%s'''" % reply)

@bot.command(name='start-listener', pass_context=True)
async def start_tcpdump(ctx):
	# c = 'iface=$(ip route get 1.1.1.1 | awk {print $5; exit});'
	# c+= f'tcpdump -ne -i $iface -Q in host {SERVE} and port 8080 -w honey.pcap'
	c = f"ssh {HOSTN}@{SERVE} bash listen.sh &"
	reply = utils.arr2str(utils.cmd(c,False))
	await ctx.send("'''%s'''" % reply)

@bot.command(name='kill-listener',pass_context=True)
async def kill_tcpdump(ctx):
	c = f"ssh {HOSTN}@{SERVE} kill -9 $(pidof tcpdump)"
	reply = utils.arr2str(utils.cmd(c,False))
	await ctx.send("'''%s'''" % reply)	

@bot.command(name='scan', pass_context=True)
async def scan_host(ctx, ip):
	await ctx.send('*Scanning* **%s**' % ip)
	c = 'nmap -sV %s' % ip
	result = '```' + (utils.arr2str(utils.cmd(c,False)))+'```'
	await ctx.send(result)

@bot.command(name='alert-me', pass_context=True)
async def set_alarm(ctx, filename):
	try:
		c = f"sftp {HOSTN}@{SERVE}:/home/{HOSTN}/HomeAlone/code/logs/web/ <<< $'get {filename}'\n"
		c += f"ssh {HOSTN}@{SERVER} echo '{PATH}' >> /home/{HOSTN}/HomeAlone/code/filelist.txt\n"
	
		utils.arr2str(utils.cmd(c,False))
		PATH = f'/home/{HOSTN}/HomeAlone/code/logs/web/{filename}'
		utils.cmd(c2)
		n = int(utils.cmd("cat %s| grep 'Connection at ' | wc -l" % filename, False).pop())
		await ctx.send(':ok_hand: *Setting Alarm on %s*, which currently has **%d** entries.' % (filename, n))
		ARMED = True
		bot.loop.create_task(check_alarm(ctx,filename,n))
	except:
		c = 'ssh %s@%s ls -la HomeAlone/code/logs/web/'% (HOSTN,SERVE)
		result = 'Something went wrong... Select one of these to set alarm on:\n'
		result += '```' + (utils.arr2str(utils.cmd(c,False)))+'```'	
		pass

@bot.command(name='is-honeypot-online', pass_context=True)
async def report_pot_state(ctx):
	if not isPotActive():
		await ctx.send('Honeypot is **Offline**')
	else:
		await ctx.send('Honeypot is **Online**')


@bot.command(name='disarm',pass_context=True)
async def disable_alarm(ctx):
	ARMED = False
	await ctx.send('**Disabling Alarm on %s**' % (filename, n))


@bot.command(name='list-logs',pass_context=True)
async def list_log_files(ctx):
	await ctx.send('*Getting list of log files*')
	c = 'ssh %s@%s ls -la HomeAlone/code/logs/web/'% (HOSTN,SERVE)
	result = '```' + (utils.arr2str(utils.cmd(c,False)))+'```'
	try:
		await ctx.send(result)
	except:
		print(result)
		pass

@bot.command(name='delete-log', pass_context=True)
async def delete_log(ctx, logfile):
	await ctx.send('*Getting list of log files*')
	c = 'ssh %s@%s ls HomeAlone/code/logs/web/'% (HOSTN,SERVE)
	if logfile in utils.cmd(c,False):
		await ctx.send('Cool cool cool. **%s** is gone' % logfile)
		c2 = 'ssh %s@%s rm HomeAlone/code/logs/web/%s'% (HOSTN,SERVE,logfile)
		utils.cmd(c2,False)
	else:
		await ctx.send("Can't find %s" % logfile)

@bot.command(name='get-log', pass_context=True)
async def get_log(ctx, logfile):
	c = 'ssh %s@%s ls HomeAlone/code/logs/web/'% (HOSTN,SERVE)
	if logfile in utils.cmd(c,False):
		await ctx.send('Found %s. Downloading it now.' % logfile)
		c = f"sftp {HOSTN}@{SERVE}:/home/{HOSTN}/HomeAlone/code/logs/web/ <<< $'get {logfile}'"
		utils.arr2str(utils.cmd(c,False))
		await ctx.send('Finished downloading**[%d bytes]**' % os.path.getsize(os.getcwd()+'/%s' % logfile))


@bot.command(name='list-cnx', pass_context=True)
async def show_connection(ctx):
	msg = 'Aw Geez, lets see who is connected'.format(ctx.message)
	await ctx.send(msg)
	c = 'ssh %s@%s netstat -antup'% (HOSTN,SERVE)
	result = '```' + (utils.arr2str(utils.cmd(c,False)))+'```'
	try:
		await ctx.send(result)
	except:
		print(result)
		await ctx.send('```'+result.split('established)\n')[1:])
		pass


async def ping_user(ctx):
	m = "{0.author.mention}".format(ctx.message)
	await ctx.send(m)



@bot.command(name='lookup',pass_context=True)
async def ipinfo(ctx, ip):
	link = 'http://ipinfo.io/%s'%ip
	response = requests.request(method='GET', url=link)
	open('lookup.json','w').write(str(json.loads(response.text)))
	reply = open('lookup.json','r').read()
	await ctx.send('```json\n'+reply+'```')
	os.remove('lookup.json')

@bot.command(name='read-log', pass_context=True)
async def read_log(ctx, filename):
	c = f'ssh {HOSTN}@{SERVE} ls HomeAlone/code/logs/web/'
	if filename in utils.cmd(c,False):
		await ctx.send('**This will take a minute...**')
		await ctx.send('<a:rickspin:834261749846507520>')
		c = f"sftp {HOSTN}@{SERVE}:/home/{HOSTN}/HomeAlone/code/logs/web/ <<< $'get {filename}'"
		utils.arr2str(utils.cmd(c,False))
		f = open(filename, 'r')
		while True:
			piece = f.read(1024)  
			if not piece:
				break
			try:
				await ctx.send('```\n'+piece.replace(SERVE,'<removed>')+'\n```')
				time.sleep(3)
			except:
				print(result)
				pass
		f.close()
		os.remove(filename)
	else:
		await ctx.send("I can't find %s" % filename)

@bot.command(name='clear', pass_context=True)
async def clean(ctx, arg):
	# Clear messages from the the last <args> minutes
	passed = 0
	failed = 0
	async for msg in ctx.message.channel.history(limit=int(arg)+1):
		try:
			await msg.delete()
			passed += 1
		except:
			failed += 1
	print(f"[Complete] Removed {passed} messages with {failed} fails")


def main():
	bot.run(TOKEN)

if __name__ == '__main__':
	main()
