# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
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
    
    text += "⚡ **1 Day** - Zero wait, unlimited downloads\n"
    text += "🔥 **3 Days** - Best for trial (Save 55%)\n"
    text += "💎 **7 Days** - Most popular! (Save 63%)\n"
    text += "👑 **15 Days** - Extended access (Save 70%)\n"
    text += "🌟 **1 Month** - Best value! (Save 73%)\n"
    text += "🚀 **3 Months** - Ultimate deal (Save 80%)\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "**Premium Benefits:**\n"
    text += "✅ Unlimited downloads per day\n"
    text += "✅ Zero wait time (instant!)\n"
    text += "✅ Up to 101 files per batch\n"
    text += "✅ Download private content\n"
    text += "✅ Priority support\n\n"
    
    text += "📸 **After Payment:**\n"
    text += f"Send screenshot to @{SUPPORT_USERNAME}\n"
    text += f"with your User ID: `{message.from_user.id}`"
    
    # Buttons with prices
    buttons = [
        [InlineKeyboardButton("⚡ 1 Day - ₹30", callback_data="buy_1_day")],
        [InlineKeyboardButton("🔥 3 Days - ₹40", callback_data="buy_3_days")],
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
        text += "✅ Up to 101 files per batch\n"
        text += "✅ Unlimited batches\n"
        text += "✅ Download private content\n"
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
        text += "• Up to 101 files per batch\n"
        text += "• Unlimited batches\n"
        text += "• Download private content\n"
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


# ==================== ADMIN COMMANDS ====================

@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium_user(client: Client, message: Message):
    """Add premium to a user - Admin only"""
    
    # Command format: /addpremium user_id days
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply("**Usage:** `/addpremium user_id days`\n**Example:** `/addpremium 123456789 30`")
            return
        
        user_id = int(parts[1])
        days = int(parts[2])
        
        # Check if user exists
        if not await db.is_user_exist(user_id):
            await message.reply(f"❌ User with ID `{user_id}` not found in database.\nUser must start the bot first.")
            return
        
        # Determine plan name
        plan_name = f"{days} Days"
        for plan_key, plan_data in PREMIUM_PLANS.items():
            if plan_data["days"] == days:
                plan_name = plan_data["title"]
                break
        
        # Add premium
        await db.add_premium(user_id, days, plan_name)
        
        expiry = await db.get_premium_expiry(user_id)
        
        await message.reply(
            f"✅ **Premium Added Successfully!**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📦 Plan: **{plan_name}**\n"
            f"⏰ Duration: **{days} days**\n"
            f"📅 Expires: **{expiry.strftime('%d %B %Y')}**"
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
                f"✅ Up to 101 files per batch\n"
                f"✅ Unlimited batches\n"
                f"✅ Download private content\n"
                f"✅ Priority support\n\n"
                f"📅 Valid till: **{expiry.strftime('%d %B %Y')}**\n\n"
                f"Enjoy premium features! 🚀"
            )
        except:
            pass
        
    except ValueError:
        await message.reply("❌ Invalid format. Use:\n`/addpremium user_id days`")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("removepremium") & filters.user(ADMINS))
async def remove_premium_user(client: Client, message: Message):
    """Remove premium from a user - Admin only"""
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply("**Usage:** `/removepremium user_id`\n**Example:** `/removepremium 123456789`")
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
        
        await message.reply(f"✅ Premium removed from user `{user_id}`")
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                "⚠️ **Your premium subscription has ended.**\n\n"
                "To continue enjoying premium features, please renew your plan.\n\n"
                "Use /premium to see plans."
            )
        except:
            pass
        
    except ValueError:
        await message.reply("❌ Invalid user ID. Use:\n`/removepremium user_id`")
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


# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
