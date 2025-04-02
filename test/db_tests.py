import os
import sys
from dotenv import load_dotenv
import asyncio

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import *
from common.common import get_lang


async def main():
    load_dotenv()
    create_tables()
    l = get_lang(755501092)
    print(l)


asyncio.run(main())
