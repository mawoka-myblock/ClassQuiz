from unittest import IsolatedAsyncioTestCase
from get import get


class Test(IsolatedAsyncioTestCase):
    async def test_get(self):
        res = await get(query="Python")
        self.assertEqual(len(res.entities), 9)
        await get(query="Test Quiz")
        await get(query="Biologie")
        await get(query="Chemie")