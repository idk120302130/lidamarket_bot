import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot.handlers import router
from aiohttp import web
from bot.api.routes import setup_routes, auth_middleware

@web.middleware
async def simple_cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

logging.basicConfig(level=logging.INFO)

async def start_bot(dp: Dispatcher, bot: Bot):
    print("Запуск бота...")
    await dp.start_polling(bot, drop_pending_updates=True)

async def start_web_server(bot: Bot):
    print("Запуск aiohttp сервера на порту 8000...")
    app = web.Application(middlewares=[simple_cors_middleware, auth_middleware])
    app["bot"] = bot
    
    setup_routes(app)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    
    # Бесконечный цикл, чтобы сервер не закрывался
    await asyncio.Event().wait()

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    # Запускаем одновременно поллинг бота и aiohttp сервер
    await asyncio.gather(
        start_bot(dp, bot),
        start_web_server(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка приложения.")
