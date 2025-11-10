# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChannelPrivate
from database.db import db
from config import ADMINS, UPI_ID, UPI_QR_BASE64, PREMIUM_PLANS, SUPPORT_USERNAME
from datetime import datetime
import base64
import io

# ==================== USER COMMANDS ====================

@Client.on_message(filters.command("premium") & filters.private)
async def show_premium_plans(client: Client, message: Message):
    """Show all premium plans with price buttons"""
    
    # Build premium plans message
    text = "╔═══════════════════════════╗\n"
    text += "   💎 PREMIUM PLANS 💎\n"
    text += "╚═══════════════════════════╝\n\n"
    
    text += "**Choose your plan below:**\n\n"
    
    text += "⚡ **3 Hours** - Quick trial (₹15 only!)\n"
    text += "🔥 **1 Day** - Zero wait, unlimited downloads\n"
    text += "💥 **3 Days** - Best for trial (Save 55%)\n"
    text += "💎 **7 Days** - Most popular! (Save 63%)\n"
    text += "👑 **15 Days** - Extended access (Save 70%)\n"
    text += "🌟 **1 Month** - Best value! (Save 73%)\n"
    text += "🚀 **3 Months** - Ultimate deal (Save 80%)\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "**Premium Benefits:**\n"
    text += "✅ Unlimited downloads per day\n"
    text += "✅ Zero wait time (instant!)\n"
    text += "✅ Up to 1000 files per batch\n"
    text += "✅ Download private content\n"
    text += "✅ Set your own channel (/setchannel)\n"
    text += "✅ Priority support\n\n"
    
    text += "📸 **After Payment:**\n"
    text += f"Send screenshot to @{SUPPORT_USERNAME}\n"
    text += f"with your User ID: `{message.from_user.id}`"
    
    # Buttons with prices
    buttons = [
        [InlineKeyboardButton("⚡ 3 Hours - ₹15", callback_data="buy_3_hours")],
        [InlineKeyboardButton("🔥 1 Day - ₹30", callback_data="buy_1_day")],
        [InlineKeyboardButton("💥 3 Days - ₹40", callback_data="buy_3_days")],
        [InlineKeyboardButton("💎 7 Days - ₹80 ⭐", callback_data="buy_7_days")],
        [InlineKeyboardButton("👑 15 Days - ₹140", callback_data="buy_15_days")],
        [InlineKeyboardButton("🌟 1 Month - ₹249", callback_data="buy_30_days")],
        [InlineKeyboardButton("🚀 3 Months - ₹599", callback_data="buy_90_days")],
        [InlineKeyboardButton("💬 Contact Support", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]
    
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^buy_"))
async def show_qr_for_plan(client: Client, callback: CallbackQuery):
    """Show QR code directly when user selects a plan"""
    
    # Extract plan from callback data
    plan_key = callback.data.replace("buy_", "")
    
    # Get plan details
    plan_info = PREMIUM_PLANS.get(plan_key, {})
    if not plan_info:
        await callback.answer("Invalid plan selected!", show_alert=True)
        return
    
    price = plan_info["price"]
    title = plan_info["title"]
    
    if UPI_QR_BASE64 == "PASTE_YOUR_BASE64_STRING_HERE":
        await callback.answer("QR Code not configured yet. Contact admin.", show_alert=True)
        return
    
    try:
        # Decode base64 to image
        qr_image_data = base64.b64decode(UPI_QR_BASE64)
        
        caption = f"╔═══════════════════════════╗\n"
        caption += f"   💳 PAYMENT DETAILS 💳\n"
        caption += f"╚═══════════════════════════╝\n\n"
        caption += f"**Selected Plan:** {title}\n"
        caption += f"**Amount to Pay:** ₹{price}\n\n"
        caption += f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        caption += f"💳 **UPI ID:** `{UPI_ID}`\n\n"
        caption += f"📱 **Steps:**\n"
        caption += f"1. Scan QR code OR copy UPI ID\n"
        caption += f"2. Pay ₹{price}\n"
        caption += f"3. Take screenshot of payment\n"
        caption += f"4. Send to @{SUPPORT_USERNAME}\n\n"
        caption += f"📝 **Important:** Mention your User ID\n"
        caption += f"Your ID: `{callback.from_user.id}`\n\n"
        caption += f"⏰ Activation: Within 5-30 minutes"
        
        # Send QR code image
        await callback.message.reply_photo(
            photo=io.BytesIO(qr_image_data),
            caption=caption,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💬 Send Payment Proof", url=f"https://t.me/{SUPPORT_USERNAME}")
            ]])
        )
        await callback.answer(f"✅ Pay ₹{price} and send screenshot!")
    except Exception as e:
        await callback.answer("Error loading QR code. Contact support.", show_alert=True)
        print(f"QR Code error: {e}")


@Client.on_message(filters.command("myplan") & filters.private)
async def check_my_plan(client: Client, message: Message):
    """Check user's premium status"""
    
    user_id = message.from_user.id
    is_premium = await db.check_premium(user_id)
    
    if is_premium:
        expiry = await db.get_premium_expiry(user_id)
        plan = await db.get_premium_plan(user_id)
        
        days_left = (expiry - datetime.now()).days
        
        text = "╔═══════════════════════════╗\n"
        text += "   💎 YOUR PREMIUM STATUS 💎\n"
        text += "╚═══════════════════════════╝\n\n"
        text += f"✅ **Status:** Premium Active\n"
        text += f"📦 **Plan:** {plan}\n"
        text += f"📅 **Expires:** {expiry.strftime('%d %B %Y')}\n"
        text += f"⏰ **Days Left:** {days_left} days\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += "**🎉 Your Premium Benefits:**\n"
        text += "✅ Unlimited downloads per day\n"
        text += "✅ Zero wait time (instant!)\n"
        text += "✅ Up to 1000 files per batch\n"
        text += "✅ Unlimited batches\n"
        text += "✅ Download private content\n"
        text += "✅ Set custom channel (/setchannel)\n"
        text += "✅ Priority support\n"
        
        buttons = [[InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_USERNAME}")]]
    else:
        text = "╔═══════════════════════════╗\n"
        text += "   📊 YOUR CURRENT PLAN 📊\n"
        text += "╚═══════════════════════════╝\n\n"
        text += "⚠️ **Status:** Free User\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += "**⛔ Current Limits:**\n"
        text += "• Only 5 downloads per day\n"
        text += "• 30 seconds wait time\n"
        text += "• Cannot download private content\n"
        text += "• Basic support only\n\n"
        text += "**✅ Upgrade to Premium for:**\n"
        text += "• Unlimited downloads per day\n"
        text += "• Zero wait time (instant!)\n"
        text += "• Up to 1000 files per batch\n"
        text += "• Unlimited batches\n"
        text += "• Download private content\n"
        text += "• Set custom channel (/setchannel)\n"
        text += "• Priority support\n"
        
        buttons = [
            [InlineKeyboardButton("💎 Upgrade to Premium", callback_data="show_premium")],
            [InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]
    
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("show_premium"))
async def show_premium_callback(client: Client, callback: CallbackQuery):
    """Show premium plans via callback"""
    await callback.answer()
    await show_premium_plans(client, callback.message)


@Client.on_callback_query(filters.regex("my_plan"))
async def my_plan_callback(client: Client, callback: CallbackQuery):
    """Check plan via callback"""
    await callback.answer()
    await check_my_plan(client, callback.message)


@Client.on_callback_query(filters.regex("help"))
async def help_callback(client: Client, callback: CallbackQuery):
    """Show help via callback"""
    await callback.answer()
    from TechVJ.strings import HELP_TXT
    await callback.message.reply(HELP_TXT)


# ==================== CUSTOM CHANNEL COMMANDS (Premium Feature) ====================

@Client.on_message(filters.command("setchannel") & filters.private)
async def set_custom_channel(client: Client, message: Message):
    """Set custom channel for downloads - Premium Only"""
    
    user_id = message.from_user.id
    is_premium = await db.check_premium(user_id)
    
    if not is_premium:
        await message.reply(
            "⚠️ **Premium Feature Only!**\n\n"
            "This feature is available only for premium users.\n\n"
            "**Upgrade to Premium to:**\n"
            "✅ Set your own channel for downloads\n"
            "✅ Unlimited downloads per day\n"
            "✅ Zero wait time\n"
            "✅ Up to 1000 files per batch\n\n"
            "Use /premium to upgrade!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💎 Get Premium", callback_data="show_premium")
            ]])
        )
        return
    
    # Send instructions
    instructions = (
        "╔═══════════════════════════╗\n"
        "   📱 SET CUSTOM CHANNEL 📱\n"
        "╚═══════════════════════════╝\n\n"
        "**Follow these steps:**\n\n"
        "1️⃣ Create a channel or group\n"
        "   (Public or Private)\n\n"
        "2️⃣ Add this bot as admin\n"
        f"   Bot: @{(await client.get_me()).username}\n\n"
        "3️⃣ Give these permissions:\n"
        "   ✅ Post Messages\n"
        "   ✅ Edit Messages\n"
        "   ✅ Delete Messages\n\n"
        "4️⃣ Send me your channel:\n"
        "   • Channel username: @yourchannel\n"
        "   • Channel ID: -1001234567890\n"
        "   • Or forward any message from channel\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Examples:**\n"
        "`@mychannel`\n"
        "`-1001234567890`\n\n"
        "Type /cancel to cancel"
    )
    
    await message.reply(instructions)
    
    # Wait for user to send channel
    try:
        response = await client.listen(message.chat.id, filters=filters.text | filters.forwarded, timeout=300)
        
        if response.text and response.text.startswith('/cancel'):
            await response.reply("❌ **Cancelled!**")
            return
        
        # Extract channel info
        channel_input = None
        
        if response.forward_from_chat:
            # User forwarded a message from channel
            channel_input = response.forward_from_chat.id
        elif response.text:
            channel_input = response.text.strip()
            # Remove @ if present
            if channel_input.startswith('@'):
                channel_input = channel_input[1:]
        
        if not channel_input:
            await response.reply("❌ Invalid input. Please try again with /setchannel")
            return
        
        # Verify bot is admin
        try:
            chat = await client.get_chat(channel_input)
            
            # Check if bot is admin
            bot_member = await client.get_chat_member(chat.id, (await client.get_me()).id)
            
            if bot_member.status not in ["administrator", "creator"]:
                await response.reply(
                    f"❌ **Bot Not Admin!**\n\n"
                    f"Please make me admin in **{chat.title}** with these permissions:\n"
                    f"✅ Post Messages\n"
                    f"✅ Edit Messages\n"
                    f"✅ Delete Messages\n\n"
                    f"Then try again with /setchannel"
                )
                return
            
            # Check if bot can post
            if not bot_member.privileges or not bot_member.privileges.can_post_messages:
                await response.reply(
                    f"❌ **Missing Permissions!**\n\n"
                    f"I need these permissions in **{chat.title}**:\n"
                    f"✅ Post Messages\n"
                    f"✅ Edit Messages\n"
                    f"✅ Delete Messages\n\n"
                    f"Please update and try again!"
                )
                return
            
            # Save channel
            await db.set_user_channel(user_id, chat.id)
            
            await response.reply(
                f"✅ **Channel Set Successfully!**\n\n"
                f"📱 Channel: **{chat.title}**\n"
                f"🆔 ID: `{chat.id}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"All your downloads will now go to this channel!\n\n"
                f"**Commands:**\n"
                f"• /mychannel - Check current channel\n"
                f"• /removechannel - Reset to DM\n"
                f"• /setchannel - Change channel"
            )
            
        except ChatAdminRequired:
            await response.reply(
                "❌ **Bot Not Admin!**\n\n"
                "Please add me as admin first with required permissions."
            )
        except ChannelPrivate:
            await response.reply(
                "❌ **Cannot Access Channel**\n\n"
                "Make sure the bot is added to the channel and has admin rights."
            )
        except Exception as e:
            await response.reply(f"❌ Error: {str(e)}\n\nPlease check the channel and try again.")
            
    except TimeoutError:
        await message.reply("⏰ Timeout! Please try again with /setchannel")


@Client.on_message(filters.command("mychannel") & filters.private)
async def check_my_channel(client: Client, message: Message):
    """Check current channel setting"""
    
    user_id = message.from_user.id
    channel_id = await db.get_user_channel(user_id)
    
    if not channel_id:
        is_premium = await db.check_premium(user_id)
        
        text = "╔═══════════════════════════╗\n"
        text += "   📱 CHANNEL SETTINGS 📱\n"
        text += "╚═══════════════════════════╝\n\n"
        text += "📍 **Current Setting:** Your DM (Default)\n\n"
        text += "All downloads will be sent to your private messages.\n\n"
        
        if is_premium:
            text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            text += "💎 **As a Premium User:**\n"
            text += "You can set your own channel!\n\n"
            text += "Use /setchannel to set up"
            
            buttons = [[InlineKeyboardButton("📱 Set Channel", callback_data="start_setchannel")]]
        else:
            text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            text += "⚠️ **Want Custom Channel?**\n"
            text += "Upgrade to Premium to:\n"
            text += "✅ Set your own channel\n"
            text += "✅ Download to your channel directly\n"
            text += "✅ Organize downloads better\n"
            
            buttons = [[InlineKeyboardButton("💎 Get Premium", callback_data="show_premium")]]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        return
    
    # User has custom channel set
    try:
        chat = await client.get_chat(int(channel_id))
        
        text = "╔═══════════════════════════╗\n"
        text += "   📱 CHANNEL SETTINGS 📱\n"
        text += "╚═══════════════════════════╝\n\n"
        text += f"✅ **Active Channel:**\n"
        text += f"📱 Name: **{chat.title}**\n"
        text += f"🆔 ID: `{chat.id}`\n"
        
        if chat.username:
            text += f"🔗 Link: @{chat.username}\n"
        
        text += f"\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"All downloads go to this channel!\n\n"
        text += f"**Commands:**\n"
        text += f"• /setchannel - Change channel\n"
        text += f"• /removechannel - Reset to DM"
        
        buttons = [[InlineKeyboardButton("🔄 Change Channel", callback_data="start_setchannel")]]
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply(
            "⚠️ **Channel Not Accessible**\n\n"
            "I cannot access the saved channel.\n"
            "It may have been deleted or I was removed.\n\n"
            "Use /setchannel to set a new channel\n"
            "or /removechannel to reset to DM"
        )


@Client.on_message(filters.command("removechannel") & filters.private)
async def remove_custom_channel(client: Client, message: Message):
    """Remove custom channel - reset to DM"""
    
    user_id = message.from_user.id
    channel_id = await db.get_user_channel(user_id)
    
    if not channel_id:
        await message.reply(
            "ℹ️ **No Custom Channel Set**\n\n"
            "You don't have a custom channel set.\n"
            "Downloads already go to your DM.\n\n"
            "Use /setchannel to set a custom channel."
        )
        return
    
    # Remove channel
    await db.remove_user_channel(user_id)
    
    await message.reply(
        "✅ **Channel Removed Successfully!**\n\n"
        "Downloads will now be sent to your DM (private messages).\n\n"
        "Use /setchannel anytime to set a new channel."
    )


@Client.on_callback_query(filters.regex("start_setchannel"))
async def setchannel_callback(client: Client, callback: CallbackQuery):
    """Start setchannel via callback"""
    await callback.answer()
    await set_custom_channel(client, callback.message)


# ==================== ADMIN COMMANDS ====================

@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium_user(client: Client, message: Message):
    """Add premium to a user - Admin only
    Supports both days and hours:
    /addpremium user_id 0.125 (for 3 hours)
    /addpremium user_id 1 (for 1 day)
    /addpremium user_id 30 (for 30 days)
    """
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply(
                "**Usage:** `/addpremium user_id days`\n\n"
                "**Examples:**\n"
                "`/addpremium 123456789 0.125` - 3 hours\n"
                "`/addpremium 123456789 1` - 1 day\n"
                "`/addpremium 123456789 30` - 30 days"
            )
            return
        
        user_id = int(parts[1])
        days = float(parts[2])  # Changed to float to support decimals
        
        # Check if user exists
        if not await db.is_user_exist(user_id):
            await message.reply(f"❌ User with ID `{user_id}` not found in database.\nUser must start the bot first.")
            return
        
        # Determine plan name
        if days == 0.125:
            plan_name = "3 Hours"
        elif days < 1:
            hours = int(days * 24)
            plan_name = f"{hours} Hours"
        elif days == 1:
            plan_name = "1 Day"
        else:
            plan_name = f"{int(days)} Days"
            # Check if matches a predefined plan
            for plan_key, plan_data in PREMIUM_PLANS.items():
                if plan_data["days"] == days:
                    plan_name = plan_data["title"]
                    break
        
        # Add premium
        await db.add_premium(user_id, days, plan_name)
        
        expiry = await db.get_premium_expiry(user_id)
        
        # Calculate display text
        if days < 1:
            hours = int(days * 24)
            duration_text = f"{hours} hours"
        else:
            duration_text = f"{int(days)} days"
        
        await message.reply(
            f"✅ **Premium Added Successfully!**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📦 Plan: **{plan_name}**\n"
            f"⏰ Duration: **{duration_text}**\n"
            f"📅 Expires: **{expiry.strftime('%d %B %Y, %I:%M %p')}**"
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                f"🎉 **Congratulations!**\n\n"
                f"Your **{plan_name}** premium has been activated!\n\n"
                f"**🎁 Your Benefits:**\n"
                f"✅ Unlimited downloads per day\n"
                f"✅ Zero wait time (instant!)\n"
                f"✅ Up to 1000 files per batch\n"
                f"✅ Unlimited batches\n"
                f"✅ Download private content\n"
                f"✅ Set custom channel (/setchannel)\n"
                f"✅ Priority support\n\n"
                f"📅 Valid till: **{expiry.strftime('%d %B %Y, %I:%M %p')}**\n\n"
                f"Enjoy premium features! 🚀"
            )
        except:
            pass
        
    except ValueError:
        await message.reply(
            "❌ Invalid format. Use:\n"
            "`/addpremium user_id days`\n\n"
            "**Examples:**\n"
            "`/addpremium 123456789 0.125` - 3 hours\n"
            "`/addpremium 123456789 1` - 1 day"
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")


@Client.on_message(filters.command(["removepremium", "rev"]) & filters.user(ADMINS))
async def remove_premium_user(client: Client, message: Message):
    """Remove premium from a user - Admin only"""
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply("**Usage:** `/rev user_id` or `/removepremium user_id`\n**Example:** `/rev 123456789`")
            return
        
        user_id = int(parts[1])
        
        # Check if user exists
        if not await db.is_user_exist(user_id):
            await message.reply(f"❌ User with ID `{user_id}` not found.")
            return
        
        # Check if user has premium
        if not await db.check_premium(user_id):
            await message.reply(f"❌ User `{user_id}` doesn't have premium.")
            return
        
        # Remove premium
        await db.remove_premium(user_id)
        
        await message.reply(f"✅ Premium revoked from user `{user_id}`")
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                "⚠️ **Your premium subscription has been revoked.**\n\n"
                "To continue enjoying premium features, please renew your plan.\n\n"
                "Use /premium to see plans."
            )
        except:
            pass
        
    except ValueError:
        await message.reply("❌ Invalid user ID. Use:\n`/rev user_id` or `/removepremium user_id`")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("premiumusers") & filters.user(ADMINS))
async def list_premium_users(client: Client, message: Message):
    """List all premium users - Admin only"""
    
    premium_users = await db.get_all_premium_users()
    total = await db.total_premium_users()
    
    if total == 0:
        await message.reply("📊 No premium users found.")
        return
    
    text = f"╔═══════════════════════════╗\n"
    text += f"   💎 PREMIUM USERS ({total}) 💎\n"
    text += f"╚═══════════════════════════╝\n\n"
    
    count = 0
    async for user in premium_users:
        count += 1
        user_id = user.get('id')
        name = user.get('name', 'Unknown')
        plan = user.get('premium_plan', 'N/A')
        expiry = user.get('premium_expiry')
        
        if expiry:
            days_left = (expiry - datetime.now()).days
            expiry_str = expiry.strftime('%d/%m/%Y')
        else:
            days_left = 0
            expiry_str = 'N/A'
        
        text += f"**{count}.** {name}\n"
        text += f"   ID: `{user_id}`\n"
        text += f"   Plan: {plan}\n"
        text += f"   Expires: {expiry_str} ({days_left}d left)\n\n"
        
        # Send in batches of 20
        if count % 20 == 0:
            await message.reply(text)
            text = ""
    
    if text:
        await message.reply(text)


@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def show_stats(client: Client, message: Message):
    """Show bot statistics - Admin only"""
    
    total_users = await db.total_users_count()
    premium_users = await db.total_premium_users()
    free_users = total_users - premium_users
    
    text = "╔═══════════════════════════╗\n"
    text += "   📊 BOT STATISTICS 📊\n"
    text += "╚═══════════════════════════╝\n\n"
    text += f"👥 Total Users: **{total_users}**\n"
    text += f"💎 Premium Users: **{premium_users}**\n"
    text += f"🆓 Free Users: **{free_users}**\n\n"
    
    if total_users > 0:
        premium_percentage = (premium_users / total_users) * 100
        text += f"📈 Premium Rate: **{premium_percentage:.1f}%**"
    
    await message.reply(text)


# Don't Remove Credit Tg - @VJ_
