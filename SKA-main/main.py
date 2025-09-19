import asyncio

from core.core import Core

async def main():
    # 创建核心实例
    app = Core()
    
    # 启动所有服务
    await app.start()
    
    # 运行主循环
    await app.heart_beat()

if __name__ == "__main__":
    asyncio.run(main())