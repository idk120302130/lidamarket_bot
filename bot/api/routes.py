import os
from aiohttp import web
from bot.api.auth import validate_init_data
from infrastructure.database import crud
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_user_from_request(request: web.Request) -> dict | None:
    init_data = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not init_data:
        init_data = request.query.get("initData", "")
    if not init_data:
        return None
    return validate_init_data(init_data)

@web.middleware
async def auth_middleware(request: web.Request, handler):
    # Пропускаем CORS и запросы к статике
    if request.method == "OPTIONS" or not request.path.startswith("/api/"):
        return await handler(request)
        
    user_data = get_user_from_request(request)
    
    # Для тестов в браузере локально
    auth_header = request.headers.get("Authorization", "")
    if not user_data and "test_" in auth_header:
        user_id = int(auth_header.split("_")[1])
        user_data = {"id": user_id, "username": f"test_{user_id}"}
        
    if not user_data:
        return web.json_response({"error": "Unauthorized. Invalid initData."}, status=401)
        
    request["user"] = user_data
    return await handler(request)

async def get_user_profile(request: web.Request):
    user_data = request["user"]
    user = await crud.get_or_create_user(user_data["id"], user_data.get("username"))
    progress = await crud.get_user_progress(user_data["id"])
    
    await crud.add_app_open_bonus(user.id)
    user = await crud.get_or_create_user(user.id) # обновляем после бонуса
    
    return web.json_response({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "coins": user.coins,
        "level": user.level,
        "progress": [{"day": p.day_number, "unlocked_at": p.unlocked_at.isoformat(), "completed_at": p.completed_at.isoformat() if p.completed_at else None} for p in progress]
    })

async def complete_day_api(request: web.Request):
    user_data = request["user"]
    data = await request.json()
    day_number = data.get("day")
    
    success = await crud.complete_day(user_data["id"], day_number)
    return web.json_response({"success": success})

async def payment_request_api(request: web.Request):
    user_data = request["user"]
    data = await request.json()
    amount = data.get("amount")
    currency = data.get("currency")
    
    payment = await crud.create_payment_request(user_data["id"], amount, currency)
    
    bot: Bot = request.app["bot"]
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"pay_approve_{payment.id}")],
        [InlineKeyboardButton(text="❌ Отказать", callback_data=f"pay_reject_{payment.id}")]
    ])
    
    for admin_id in admin_ids:
        if admin_id.strip():
            try:
                await bot.send_message(
                    chat_id=int(admin_id.strip()),
                    text=f"💸 Заявка на оплату!\nПользователь: @{user_data.get('username', user_data['id'])}\nСумма: {amount} {currency}\nID платежа: {payment.id}",
                    reply_markup=markup
                )
            except Exception as e:
                print(f"Failed to send admin msg: {e}")
                
    return web.json_response({"success": True, "payment_id": payment.id})

async def get_referrals_api(request: web.Request):
    user_data = request["user"]
    referrals = await crud.get_referrals(user_data["id"])
    return web.json_response({
        "referrals": [{"id": r.id, "username": r.username} for r in referrals]
    })

async def mock_parser(request: web.Request):
    return web.json_response({"success": True, "message": "Товар найден. Цена 1500¥, артикул 12345."})

async def mock_calculator(request: web.Request):
    data = await request.json()
    price = float(data.get("price", 0))
    weight = float(data.get("weight", 0))
    delivery = weight * 15.0
    commission = price * 0.07
    total_yuan = price + delivery + commission
    total_rubles = total_yuan * 12.0
    return web.json_response({
        "price": price,
        "delivery": delivery,
        "commission": commission,
        "total_yuan": total_yuan,
        "total_rubles": total_rubles
    })

async def index_handler(request: web.Request):
    # Возвращаем index.html для всех не-API роутов (SPA)
    return web.FileResponse('webapp/dist/index.html')

def setup_routes(app: web.Application):
    app.router.add_get("/api/user", get_user_profile)
    app.router.add_post("/api/complete_day", complete_day_api)
    app.router.add_post("/api/payment/request", payment_request_api)
    app.router.add_get("/api/referrals", get_referrals_api)
    
    app.router.add_post("/api/parse", mock_parser)
    app.router.add_post("/api/calculate", mock_calculator)
    
    # Раздача статики React
    if os.path.exists("webapp/dist"):
        app.router.add_static("/assets", "webapp/dist/assets", name="assets")
        app.router.add_route('*', '/{path:.*}', index_handler)
