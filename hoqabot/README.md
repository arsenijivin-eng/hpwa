# HoqaBot

Telegram bot based on aiogram 3.

## Start
1. Install Python 3.11+.
2. `pip install -r requirements.txt`
3. Set environment variable `BOT_TOKEN` to the **new** token from BotFather.
4. Put the final Hoqa images in `images/` with these names:
   - `start.jpg`
   - `miss.jpg`
   - `hit.jpg`
5. Run `python bot.py`.

## Important
- The bot can verify subscription to `@hoqanft` only when Telegram allows `getChatMember`; add the bot to the channel with sufficient permissions.
- Telegram does **not** provide a reliable event saying that a user merely clicked an arbitrary external bot/link. The VPN/apply buttons are therefore normal URL buttons; the bot can verify them only if the external service provides an integration/callback.
- NFT values in this starter are placeholders; replace them with your real NFT inventory/links before production.
- Do not put a bot token directly in public source code. Use `BOT_TOKEN` as an environment variable.
