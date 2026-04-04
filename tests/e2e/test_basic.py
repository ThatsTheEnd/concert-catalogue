from nicegui.testing import User

async def test_concerts_page(user: User) -> None:
    await user.open('/concerts')
    await user.should_see('KonzertKatalog')
