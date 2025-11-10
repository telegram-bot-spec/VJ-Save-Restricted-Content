# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME, FREE_USER_DAILY_LIMIT, FREE_USER_WAIT_TIME, PREMIUM_USER_WAIT_TIME, SUPPORT_USERNAME, COMMUNITY_GROUP
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

# ==================== BATCH LIMITS ====================
PREMIUM_USER_BATCH_LIMIT = 1000  # Premium users can download up to 1000 files per batch

class batch_temp(object):
    IS_BATCH = {}

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    # Check if user is premium
    is_premium = await db.check_premium(message.from_user.id)
    
    if is_premium:
        status_text = "💎 **Premium User**"
    else:
        status_text = "🆓 **Free User** - Upgrade to Premium!"
    
    buttons = [[
        InlineKeyboardButton("🌟 Get Premium", callback_data="show_premium")
    ],[
        InlineKeyboardButton('❓ Help', callback_data='help'),
        InlineKeyboardButton('📊 My Plan', callback_data='my_plan')
    ],[
        InlineKeyboardButton('👥 Join Group', url=COMMUNITY_GROUP),
        InlineKeyboardButton('💬 Support', url=f'https://t.me/{SUPPORT_USERNAME}')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention},\n\nI am Save Restricted Content Bot. I can send you restricted content by its post link.\n\n{status_text}\n\nFor downloading restricted content /login first.\n\nKnow how to use bot: /help\n\n⚡ Want INSTANT downloads with NO limits?\n💎 Upgrade to Premium: /premium</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if user is premium
    is_premium = await db.check_premium(user_id)
    
    # Joining chat
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e: 
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        
        total_files = toID - fromID + 1
        
        # ==================== CHECK LIMITS BEFORE STARTING ====================
        if not is_premium:
            # Check daily limit for free users
            downloads_today = await db.get_daily_downloads(user_id)
            remaining_today = FREE_USER_DAILY_LIMIT - downloads_today
            
            if remaining_today <= 0:
                await message.reply(
                    f"⚠️ **Daily Limit Reached!**\n\n"
                    f"You have used all **{FREE_USER_DAILY_LIMIT}** downloads for today.\n\n"
                    f"**Upgrade to Premium for:**\n"
                    f"✅ Unlimited Downloads\n"
                    f"✅ Zero Wait Time\n"
                    f"✅ Up to 1000 files per batch\n"
                    f"✅ Priority Support\n\n"
                    f"Use /premium to upgrade!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("💎 Upgrade Now", callback_data="show_premium")
                    ]])
                )
                return
            
            # Check if user is trying to download more files than they have remaining
            if total_files > remaining_today:
                await message.reply(
                    f"⚠️ **Not Enough Downloads Left!**\n\n"
                    f"You're trying to download **{total_files} files**\n"
                    f"But you only have **{remaining_today}/{FREE_USER_DAILY_LIMIT}** downloads left today.\n\n"
                    f"**Options:**\n"
                    f"1️⃣ Download only {remaining_today} files today\n"
                    f"2️⃣ Wait until tomorrow for limit reset\n"
                    f"3️⃣ Upgrade to Premium for unlimited downloads!\n\n"
                    f"💎 Use /premium to upgrade",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("💎 Get Unlimited Downloads", callback_data="show_premium")
                    ]])
                )
                return
        else:
            # Premium user - check batch limit
            if total_files > PREMIUM_USER_BATCH_LIMIT:
                await message.reply(
                    f"⚠️ **Batch Limit Exceeded!**\n\n"
                    f"You're trying to download **{total_files} files**\n"
                    f"Premium limit: **{PREMIUM_USER_BATCH_LIMIT} files per batch**\n\n"
                    f"💡 **Tip:** Split into smaller batches:\n"
                    f"Batch 1: `{fromID}-{fromID + PREMIUM_USER_BATCH_LIMIT - 1}`\n"
                    f"Batch 2: `{fromID + PREMIUM_USER_BATCH_LIMIT}-{toID}`"
                )
                return

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                return
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except:
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        else:
            if TechVJUser is None:
                await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                return
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        
        # ==================== PROGRESS TRACKING VARIABLES ====================
        total_files_to_download = toID - fromID + 1
        successfully_downloaded = 0
        failed_downloads = 0
        progress_msg = None
        last_progress_update = 0
        
        # Send initial progress message
        progress_msg = await message.reply(
            f"📥 **Starting Batch Download...**\n\n"
            f"📊 Total Files: **{total_files_to_download}**\n"
            f"✅ Downloaded: **0**\n"
            f"❌ Failed: **0**\n"
            f"⏳ Remaining: **{total_files_to_download}**"
        )
        
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): 
                # User cancelled
                if progress_msg:
                    await progress_msg.edit(
                        f"🛑 **Download Cancelled**\n\n"
                        f"📊 Total: {total_files_to_download}\n"
                        f"✅ Downloaded: {successfully_downloaded}\n"
                        f"❌ Failed: {failed_downloads}"
                    )
                break
            
            # Get user's custom channel or default to DM
            user_channel = await db.get_user_channel(user_id)
            if user_channel:
                chat = int(user_channel)
            elif CHANNEL_ID:
                chat = int(CHANNEL_ID) if CHANNEL_ID else message.chat.id
            else:
                chat = message.chat.id
            
            try:
                # private
                if "https://t.me/c/" in message.text:
                    chatid = int("-100" + datas[4])
                    await handle_private(client, acc, message, chatid, msgid, chat)
                    successfully_downloaded += 1
        
                # bot
                elif "https://t.me/b/" in message.text:
                    username = datas[4]
                    await handle_private(client, acc, message, username, msgid, chat)
                    successfully_downloaded += 1
                
                # public
                else:
                    username = datas[3]
                    try:
                        msg = await client.get_messages(username, msgid)
                    except UsernameNotOccupied: 
                        await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                        failed_downloads += 1
                        continue
                    try:
                        await client.copy_message(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)
                        successfully_downloaded += 1
                    except:
                        try:    
                            await handle_private(client, acc, message, username, msgid, chat)
                            successfully_downloaded += 1
                        except Exception as e:
                            failed_downloads += 1
                            if ERROR_MESSAGE == True:
                                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                
                # Increment download counter for free users ONLY on success
                if not is_premium:
                    await db.increment_daily_downloads(user_id)
                
            except FloodWait as e:
                # ==================== AUTO FLOODWAIT HANDLER ====================
                wait_time = e.value + 2  # Add 2 second buffer
                if progress_msg:
                    await progress_msg.edit(
                        f"⚠️ **FloodWait Detected**\n\n"
                        f"Telegram rate limit hit!\n"
                        f"⏳ Auto-waiting for **{wait_time}** seconds...\n\n"
                        f"📊 Progress so far:\n"
                        f"✅ Downloaded: {successfully_downloaded}/{total_files_to_download}\n"
                        f"❌ Failed: {failed_downloads}\n\n"
                        f"Bot will continue automatically..."
                    )
                await asyncio.sleep(wait_time)
                # Retry the same file after waiting
                try:
                    if "https://t.me/c/" in message.text:
                        chatid = int("-100" + datas[4])
                        await handle_private(client, acc, message, chatid, msgid, chat)
                    elif "https://t.me/b/" in message.text:
                        username = datas[4]
                        await handle_private(client, acc, message, username, msgid, chat)
                    else:
                        username = datas[3]
                        msg = await client.get_messages(username, msgid)
                        await client.copy_message(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)
                    successfully_downloaded += 1
                    if not is_premium:
                        await db.increment_daily_downloads(user_id)
                except:
                    failed_downloads += 1
            except Exception as e:
                failed_downloads += 1
                if ERROR_MESSAGE == True:
                    print(f"Error downloading file {msgid}: {e}")

            # ==================== PROGRESS UPDATE EVERY 50 FILES ====================
            current_file = msgid - fromID + 1
            if current_file - last_progress_update >= 50 or current_file == total_files_to_download:
                last_progress_update = current_file
                remaining = total_files_to_download - successfully_downloaded - failed_downloads
                
                if progress_msg:
                    try:
                        await progress_msg.edit(
                            f"📥 **Downloading in Progress...**\n\n"
                            f"📊 Total Files: **{total_files_to_download}**\n"
                            f"✅ Downloaded: **{successfully_downloaded}**\n"
                            f"❌ Failed: **{failed_downloads}**\n"
                            f"⏳ Remaining: **{remaining}**\n\n"
                            f"📈 Progress: **{(current_file/total_files_to_download*100):.1f}%**"
                        )
                    except:
                        pass

            # Wait time based on premium status
            if is_premium:
                wait_time = PREMIUM_USER_WAIT_TIME  # From config (0 seconds for premium)
            else:
                wait_time = FREE_USER_WAIT_TIME  # 30 seconds for free users
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # ==================== FINAL SUMMARY ====================
        if progress_msg:
            success_rate = (successfully_downloaded / total_files_to_download * 100) if total_files_to_download > 0 else 0
            
            summary_text = f"{'🎉' if failed_downloads == 0 else '✅'} **Batch Download Complete!**\n\n"
            summary_text += f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            summary_text += f"📊 **Summary:**\n"
            summary_text += f"📁 Total Files: **{total_files_to_download}**\n"
            summary_text += f"✅ Successfully Downloaded: **{successfully_downloaded}**\n"
            summary_text += f"❌ Failed: **{failed_downloads}**\n"
            summary_text += f"📈 Success Rate: **{success_rate:.1f}%**\n\n"
            
            if not is_premium:
                downloads_left = FREE_USER_DAILY_LIMIT - await db.get_daily_downloads(user_id)
                summary_text += f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                summary_text += f"📊 Downloads left today: **{downloads_left}/{FREE_USER_DAILY_LIMIT}**\n\n"
                if downloads_left == 0:
                    summary_text += f"💎 Want unlimited downloads? /premium"
            
            await progress_msg.edit(summary_text)
            
        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int, chat: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        await smsg.delete()
        raise e
    
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            raise e
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
