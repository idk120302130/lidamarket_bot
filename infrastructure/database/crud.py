from sqlalchemy import select
from infrastructure.database.models import User, DayProgress, Payment, Transaction
from infrastructure.database.database import async_session
from datetime import datetime, timedelta

def get_level(coins: int) -> str:
    if coins < 50:
        return "Новичок"
    elif coins < 200:
        return "Исследователь"
    return "Товарный барон"

async def get_or_create_user(user_id: int, username: str = None, referrer_id: int = None):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаем пользователя
            user = User(id=user_id, username=username, referrer_id=referrer_id)
            session.add(user)
            await session.commit()
            
            # Инициализируем 1 день
            day1 = DayProgress(user_id=user_id, day_number=1, unlocked_at=datetime.utcnow())
            session.add(day1)
            
            # Начисляем монеты рефереру
            if referrer_id:
                referrer_res = await session.execute(select(User).where(User.id == referrer_id))
                referrer = referrer_res.scalar_one_or_none()
                if referrer:
                    referrer.coins += 50
                    referrer.level = get_level(referrer.coins)
                    tx = Transaction(user_id=referrer.id, type="earn", amount=50, description="Бонус за реферала")
                    session.add(tx)
            
            await session.commit()
            await session.refresh(user)
        return user

async def add_app_open_bonus(user_id: int):
    # Даем 5 монет за открытие приложения (раз в день или каждый раз - для простоты пока дадим 5 монет)
    # В реальном приложении нужно проверять дату последнего открытия
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.coins += 5
            user.level = get_level(user.coins)
            tx = Transaction(user_id=user_id, type="earn", amount=5, description="Бонус за вход в App")
            session.add(tx)
            await session.commit()

async def get_user_progress(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(DayProgress).where(DayProgress.user_id == user_id).order_by(DayProgress.day_number))
        return result.scalars().all()

async def complete_day(user_id: int, day_number: int):
    async with async_session() as session:
        res = await session.execute(select(DayProgress).where(DayProgress.user_id == user_id, DayProgress.day_number == day_number))
        day = res.scalar_one_or_none()
        if day and not day.completed_at:
            day.completed_at = datetime.utcnow()
            
            # Открываем следующий день через 24 часа
            if day_number < 7:
                res_next = await session.execute(select(DayProgress).where(DayProgress.user_id == user_id, DayProgress.day_number == day_number + 1))
                next_day = res_next.scalar_one_or_none()
                if not next_day:
                    next_day = DayProgress(user_id=user_id, day_number=day_number + 1, unlocked_at=datetime.utcnow() + timedelta(hours=24))
                    session.add(next_day)
            
            # Начисляем монеты за день
            user_res = await session.execute(select(User).where(User.id == user_id))
            user = user_res.scalar_one()
            user.coins += 10
            user.level = get_level(user.coins)
            
            tx = Transaction(user_id=user_id, type="earn", amount=10, description=f"Выполнение задания дня {day_number}")
            session.add(tx)
            
            await session.commit()
            return True
        return False

async def create_payment_request(user_id: int, amount: float, currency: str):
    async with async_session() as session:
        payment = Payment(user_id=user_id, amount=amount, currency=currency)
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

async def approve_payment(payment_id: int):
    async with async_session() as session:
        res = await session.execute(select(Payment).where(Payment.id == payment_id))
        payment = res.scalar_one_or_none()
        if payment and payment.status == "pending":
            payment.status = "approved"
            
            user_res = await session.execute(select(User).where(User.id == payment.user_id))
            user = user_res.scalar_one()
            user.role = "student"
            
            # Мгновенно открываем все 7 дней
            for i in range(1, 8):
                d_res = await session.execute(select(DayProgress).where(DayProgress.user_id == user.id, DayProgress.day_number == i))
                d = d_res.scalar_one_or_none()
                if not d:
                    new_d = DayProgress(user_id=user.id, day_number=i, unlocked_at=datetime.utcnow())
                    session.add(new_d)
                else:
                    if d.unlocked_at > datetime.utcnow():
                        d.unlocked_at = datetime.utcnow()
            
            await session.commit()
            return True
        return False

async def reject_payment(payment_id: int):
    async with async_session() as session:
        res = await session.execute(select(Payment).where(Payment.id == payment_id))
        payment = res.scalar_one_or_none()
        if payment and payment.status == "pending":
            payment.status = "rejected"
            await session.commit()
            return True
        return False

async def get_referrals(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.referrer_id == user_id))
        return result.scalars().all()
