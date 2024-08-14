from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crud.token_crud import remove_token

scheduler = AsyncIOScheduler()


def schedule_job(session, token, ACCESS_TOKEN_EXPIRE_SECONDS):
    job_id = scheduler.add_job(
        remove_token,
        "interval",
        seconds=ACCESS_TOKEN_EXPIRE_SECONDS,
        args=[session, token, scheduler],
    )
    return job_id


scheduler.start()
