@echo off
title Career Agent - Setup
echo ==========================================
echo  Career Agent - Installing dependencies
echo ==========================================
echo.

pip install --upgrade pip
pip install requests pyyaml python-telegram-bot reportlab

echo.
echo ==========================================
echo  All dependencies installed!
echo.
echo  NEXT STEPS:
echo  1. Open config.yaml and fill in your details
echo  2. Get a Telegram bot token from @BotFather
echo  3. Get your chat_id from @userinfobot
echo  4. Paste both into config.yaml
echo  5. Run START_AGENT.bat to launch
echo ==========================================
echo.
pause
