"""
main.py — запускает API-сервер и бота в одном процессе.
Используется для деплоя на Railway / Render / любой хостинг.
"""
import os
import threading
import uvicorn
import db
from bot import build_app   # импортируем фабрику приложения

def run_api():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="warning")

def main():
    db.init_db()

    # API-сервер в отдельном потоке
    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    print("🌐 API запущен")

    # Бот в основном потоке
    print("🤖 Бот запущен")
    app = build_app()
    app.run_polling()

if __name__ == "__main__":
    main()
