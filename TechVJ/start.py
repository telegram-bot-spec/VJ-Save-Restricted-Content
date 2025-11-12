# Ask Doubt on telegram @aryansmilezzz

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, WAITING_TIME, FREE_USER_DAILY_LIMIT, FREE_USER_WAIT_TIME, PREMIUM_USER_WAIT_TIME, SUPPORT_USERNAME, COMMUNITY_GROUP, MAX_BATCH_SIZE_PREMIUM, PROGRESS_UPDATE_INTERVAL
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser
from datetime import datetime

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
        # Check daily limit for free users
        if not is_premium:
            can_download = await db.check_daily_limit(user_id, FREE_USER_DAILY_LIMIT)
            if not can_download:
                downloads_today = await db.get_daily_downloads(user_id)
                await message.reply(
                    f"⚠️ **Daily Limit Reached!**\n\n"
                    f"You have used all **{FREE_USER_DAILY_LIMIT}** downloads for today.\n\n"
                    f"**Upgrade to Premium for:**\n"
                    f"✅ Unlimited Downloads\n"
                    f"✅ Zero Wait Time\n"
                    f"✅ Up to {MAX_BATCH_SIZE_PREMIUM} files per batch\n"
                    f"✅ Priority Support\n\n"
                    f"Use /premium to upgrade!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("💎 Upgrade Now", callback_data="show_premium")
                    ]])
                )
                return
        
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        
        # Check batch size for premium users
        total_files = toID - fromID + 1
        if is_premium and total_files > MAX_BATCH_SIZE_PREMIUM:
            await message.reply(
                f"⚠️ **Batch size too large!**\n\n"
                f"Requested: {total_files} files\n"
                f"Maximum: {MAX_BATCH_SIZE_PREMIUM} files per batch\n\n"
                f"Please split into smaller batches."
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
        
        # Initialize progress tracking
        batch_temp.IS_BATCH[message.from_user.id] = False
        successful_downloads = 0
        failed_downloads = 0
        total_files = toID - fromID + 1
        start_time = datetime.now()
        
        # Send initial progress message
        progress_msg = await message.reply(f"📥 **Starting batch download...**\n\nTotal files: {total_files}")
        
        # Increment download counter for free users (count the batch as 1 download)
        if not is_premium:
            await db.increment_daily_downloads(user_id)
        
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): 
                break
            
            current_file = msgid - fromID + 1
            
            try:
                # private
                if "https://t.me/c/" in message.text:
                    chatid = int("-100" + datas[4])
                    await handle_private(client, acc, message, chatid, msgid)
                    successful_downloads += 1
        
                # bot
                elif "https://t.me/b/" in message.text:
                    username = datas[4]
                    await handle_private(client, acc, message, username, msgid)
                    successful_downloads += 1
                
                # public
                else:
                    username = datas[3]
                    try:
                        msg = await client.get_messages(username, msgid)
                    except UsernameNotOccupied: 
                        await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                        return
                    try:
                        await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                        successful_downloads += 1
                    except:
                        try:    
                            await handle_private(client, acc, message, username, msgid)
                            successful_downloads += 1
                        except Exception as e:
                            failed_downloads += 1
                            if ERROR_MESSAGE == True:
                                await client.send_message(message.chat.id, f"Error on file {msgid}: {e}", reply_to_message_id=message.id)
            
            except FloodWait as e:
                # Handle FloodWait - wait exactly as Telegram says
                wait_time = e.value
                await progress_msg.edit(f"⏳ **FloodWait Detected!**\n\nWaiting {wait_time} seconds as requested by Telegram...\n\nProgress: {current_file}/{total_files}")
                await asyncio.sleep(wait_time)
                # Retry the same file
                try:
                    if "https://t.me/c/" in message.text:
                        chatid = int("-100" + datas[4])
                        await handle_private(client, acc, message, chatid, msgid)
                        successful_downloads += 1
                    elif "https://t.me/b/" in message.text:
                        username = datas[4]
                        await handle_private(client, acc, message, username, msgid)
                        successful_downloads += 1
                    else:
                        username = datas[3]
                        msg = await client.get_messages(username, msgid)
                        await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                        successful_downloads += 1
                except Exception as retry_error:
                    failed_downloads += 1
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error on file {msgid} (retry): {retry_error}", reply_to_message_id=message.id)
            
            except Exception as e:
                # Skip failed file and continue
                failed_downloads += 1
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error on file {msgid}: {e}", reply_to_message_id=message.id)
            
            # Update progress every PROGRESS_UPDATE_INTERVAL files
            if current_file % PROGRESS_UPDATE_INTERVAL == 0 or current_file == total_files:
                percentage = int((current_file / total_files) * 100)
                try:
                    await progress_msg.edit(
                        f"📥 **Downloading...**\n\n"
                        f"Progress: {current_file}/{total_files} ({percentage}%)\n"
                        f"✅ Success: {successful_downloads}\n"
                        f"❌ Failed: {failed_downloads}"
                    )
                except:
                    pass
            
            # No artificial wait time - let Telegram handle speed naturally
            # Only wait if FloodWait occurs (handled above)
        
        # Calculate time taken
        end_time = datetime.now()
        time_taken = end_time - start_time
        minutes = int(time_taken.total_seconds() / 60)
        seconds = int(time_taken.total_seconds() % 60)
        
        # Send final summary
        summary = f"✅ **Batch Complete!**\n\n"
        summary += f"📊 **Summary:**\n"
        summary += f"✅ Downloaded: {successful_downloads} files\n"
        summary += f"❌ Failed: {failed_downloads} files\n"
        summary += f"📦 Total: {total_files} files\n"
        summary += f"⏱️ Time: {minutes}m {seconds}s"
        
        try:
            await progress_msg.edit(summary)
        except:
            await message.reply(summary)
        
        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass
        
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    
    # Send everything to user's DM
    chat = message.chat.id
    
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**')
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    
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
            await client.send_document(chat, file, thumb=ph_path, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", parse_mode=enums.ParseMode.HTML)
    
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
