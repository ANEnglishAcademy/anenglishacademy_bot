# Privacy Policy — SpeakEasy (@BlaBlaEnglishBot)

**Last updated:** 2025-09-23

## What we collect
- Messages you send to the bot are processed in memory to deliver features:
  - Command handling (e.g., `/translate`, `/help`)
  - Translation requests forwarded to the translation provider you configure
- We do not create persistent user profiles or store chat histories on our servers.

## Translation service
- By default, the bot uses **LibreTranslate** (`TRANSLATE_URL`) for EN⇄RU translations.
- Your text is transmitted to that service solely for translation and returned to you.
- If you replace the translation provider, your text will be sent to that provider instead.
- Please review the privacy policy of your chosen provider.

## Data retention
- We do not persist user messages or translations in a database.
- Temporary logs may include metadata (timestamps, command names) for debugging. We avoid logging message content.

## Third parties
- Telegram receives your messages as part of normal bot operation. See Telegram’s privacy policy.
- Your chosen translation provider receives text you request to translate.

## Security
- The bot token and admin ID are kept as environment variables, not in code.
- We recommend hosting providers’ standard network and secrets management.

## Your choices
- You can stop using the bot at any time and delete your messages in your Telegram client.
- To avoid sending sensitive information to third parties, do not submit confidential data for translation.

## Contact
For privacy requests, contact the bot owner via Telegram: @BlaBlaEnglishBot (type `/about` for info).
