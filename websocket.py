import asyncio
import websockets
import logging
import configparser

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')
HOST = config.get('Server', 'HOST', fallback='localhost')
PORT = config.getint('Server', 'PORT', fallback=8765)


# 处理 WebSocket 连接
async def handle_connection(websocket, path):
    logging.info(f"新的 WebSocket 连接: {websocket.remote_address}")

    try:
        # 添加心跳机制
        async def send_heartbeat():
            while True:
                await asyncio.sleep(30)  # 每 30 秒发送一次心跳
                try:
                    await websocket.send('{"type": "heartbeat"}')
                except websockets.exceptions.ConnectionClosed:
                    break

        # 启动心跳任务
        heartbeat_task = asyncio.create_task(send_heartbeat())

        # 设置心跳超时时间
        HEARTBEAT_TIMEOUT = 300  # 300秒内如果没有收到心跳则认为连接超时
        last_heartbeat = asyncio.get_running_loop().time()

        async for message in websocket:
            logging.info(f"收到消息: {message}")

            # 处理心跳消息
            if message == '{"type": "heartbeat"}':
                last_heartbeat = asyncio.get_running_loop().time()
                continue

            # 这里可以添加你的消息处理逻辑，比如解析 JSON
            response = f"服务器收到: {message}"

            # 发送消息给客户端
            await websocket.send(response)

        # 确保心跳任务在连接关闭时取消
        heartbeat_task.cancel()
        await heartbeat_task

    except websockets.exceptions.ConnectionClosed as e:
        logging.warning(f"连接关闭: {websocket.remote_address}, 原因: {e.reason} (code: {e.code})")
        # 确保心跳任务在连接关闭时取消
        if not heartbeat_task.done():
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        logging.error(f"发生错误: {e}")


# 启动 WebSocket 服务器
async def start_server():
    server = await websockets.serve(handle_connection, HOST, PORT)
    logging.info(f"WebSocket 服务器已启动，监听 {HOST}:{PORT}")
    await server.wait_closed()


# 运行服务器
if __name__ == "__main__":
    asyncio.run(start_server())