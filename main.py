import asyncio
import os
from opentele.tl import TelegramClient
from opentele.api import API
import time
from config import *
import random
import colorama
from colorama import Fore
colorama.init()

import subprocess, requests

from telethon.errors import FloodWaitError
from telethon import errors



class Result:
	total_accs = 0 #всего аккаунтов
	valid_accs = 0 #валидных аккаунтов
	total_msg = 0 #всего отправлено
	successful_msg = 0 #успешно отправлено
	error_msg = 0 #не отправлено


def random_proxy():
	lines = open(PROXY_FILE, 'r').read().split('\n')
	proxy_line = random.choice(lines)

	if proxy_line == '':
		proxy_line = random.choice(lines)

	try:
		proxy_rand = {
			'proxy_type': 'socks5',
			'addr': proxy_line.split(':')[0],
			'port': int(proxy_line.split(':')[1]),
			'username': proxy_line.split(':')[2],
			'password': proxy_line.split(':')[3],
			'rdns': True}
	except IndexError:
		return random_proxy()

	return proxy_rand


async def spam(session_path: str):
	Result.total_accs += 1

	if USE_PROXY == 'True':
		proxy = random_proxy()
	else:
		proxy = None

	try:
		client = TelegramClient(os.path.join('sessions', session_path), proxy=proxy)
		await client.connect()
		info = await client.get_me()

		if info != None:
			dialogs = await client.get_dialogs()
			Result.valid_accs += 1

			for dialog in dialogs:				
				send_entity = await client.get_entity(dialog.id)
				send_entity_for_analize = str(send_entity)

				if "User(id=" in send_entity_for_analize:
					if send_entity.bot == False:
						#дейтсвие над чатом

						try:
							query = await client.inline_query("@PostBot", POST_BOT_HASH)
							msg = await query[0].click(send_entity)
							await asyncio.sleep(0.5)
							await client.delete_messages(entity=dialog.id, revoke=False, message_ids=msg.id)
							await asyncio.sleep(1)
							print(Fore.GREEN + f'Сообщение отправлено (ЛС) ({session_path}) -> {dialog.id}')
							Result.successful_msg += 1
							Result.total_msg += 1
						except Exception as e:
							error_for_analize = str(e)
							if "seconds is required" in error_for_analize:
								break
							else:	
								print(Fore.RED + f'Ошибка (ЛС) ({session_path}) -> {e}')
								Result.error_msg += 1
								Result.total_msg += 1

				elif "Channel(id=" in send_entity_for_analize:
					if send_entity.megagroup == True:
						#действие над мегагруппой

						try:
							query = await client.inline_query("@PostBot", POST_BOT_HASH)
							msg = await query[0].click(send_entity)
							await asyncio.sleep(0.5)
							print(Fore.GREEN + f'Сообщение отправлено (МЕГАГРУППА) ({session_path}) -> {dialog.id}')
							Result.successful_msg += 1
							Result.total_msg += 1
						except Exception as e:
							error_for_analize = str(e)
							if "seconds is required" in error_for_analize:
								break
							else:
								print(Fore.RED + f'Ошибка (МЕГАГРУППА) ({session_path}) -> {e}')
								Result.error_msg += 1
								Result.total_msg += 1

			if client.is_connected():
				await client.disconnect()

		else:
			print(Fore.RED + f'Аккаунт невалид -> {session_path}')
			if client.is_connected():
				await client.disconnect()

	except:
		print(Fore.RED + f'Не удалось подключиться -> {session_path}')
		if client.is_connected():
			await client.disconnect()



async def main():
	sessionFolder = r"sessions/"
	tasks = []
	loop = asyncio.get_event_loop()

	no_concurrent = 20
	dltasks = set()

	for session_spam in os.listdir(sessionFolder):
		model = session_spam.split('.')[1]
		if model == 'session':

			if len(dltasks) >= no_concurrent:
				_done, dltasks = await asyncio.wait(
				dltasks, return_when=asyncio.FIRST_COMPLETED)

			dltasks.add(loop.create_task(spam(session_spam)))

	await asyncio.wait(dltasks)


	print(Fore.WHITE + f'\n\nВсего аккаунтов: {str(Result.total_accs)}')
	print(Fore.GREEN + f'Валидных аккаунтов: {str(Result.valid_accs)}')
	print(Fore.WHITE + f'\nВсего отправлено: {str(Result.total_msg)}')
	print(Fore.GREEN + f'Успешно отправлено: {str(Result.successful_msg)}')
	print(Fore.RED + f'Не отправлено: {str(Result.error_msg)}')

if __name__ == '__main__':
	asyncio.run(main())