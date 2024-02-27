from tortoise import Tortoise, run_async


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url="postgres://postgres:poker123@localhost:5432",
        modules={"models": ["models.account"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas()


run_async(init())
