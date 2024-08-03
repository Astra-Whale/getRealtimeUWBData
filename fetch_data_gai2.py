import asyncio
import websockets
import json
import os
import time
import logging
import logging.handlers
import threading
import queue

# 创建一个队列来存放日志记录
log_queue = queue.Queue()

# 自定义的日志处理器，使用队列
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

# 日志记录线程函数
def log_listener(queue):
    while True:
        record = queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)

# 配置日志记录器，在这里配置日志等级
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  
logger = logging.getLogger(__name__)

# 添加自定义的QueueHandler
queue_handler = QueueHandler(log_queue)
logger.addHandler(queue_handler)

# 启动日志记录线程
log_thread = threading.Thread(target=log_listener, args=(log_queue,))
log_thread.start()

class RatioLogger:
    def __init__(self, logger, rate=10, high_level=logging.INFO, low_level=logging.DEBUG):
        self.logger = logger
        self.rate = rate
        self.counter = 0
        self.high_level = high_level
        self.low_level = low_level

    def log(self, msg, *args, **kwargs):
        self.counter += 1
        if self.counter % self.rate == 0:
            self.logger.log(self.high_level, msg, *args, **kwargs)
        else:
            self.logger.log(self.low_level, msg, *args, **kwargs)

rate_limited_logger = RatioLogger(logger, rate=50, high_level=logging.INFO, low_level=logging.DEBUG)

# 从url拉取websocket
async def get_wss_data(url):
    os.makedirs("./data", exist_ok=True)  # Ensure the data directory exists
    
    async with websockets.connect(url) as websocket:
        while True:
            formatted_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            filename = f"./data/{formatted_time}.json"
            rate_limited_logger.log(f"\n{filename}")  # Log the new filename
            
            while True:
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    json_data = json.loads(data)  # Directly parse the received data
                    
                    if json_data.get("game", {}).get("countdown") == 0 or json_data.get("game", {}).get("progress") != 5:  # Check if the game is going on
                        rate_limited_logger.log(f'\ngameProgress: {json_data["game"]["progress"]}\ncountdown: {json_data["game"]["countdown"]}\nNot in game\n')
                        break
                    
                    # Write data to file
                    with open(filename, 'a') as file:
                        json.dump(json_data, file, indent=4)
                        file.write(',\n')
                        rate_limited_logger.log(f'\n\ncountdown: {json_data["game"]["countdown"]}\n')
                
                except asyncio.TimeoutError:
                    rate_limited_logger.log("\nNo data received in the last 5 seconds")
                except (json.JSONDecodeError, KeyError) as e:
                    rate_limited_logger.log(f"\nData parsing error: {e}")
                except Exception as e:
                    rate_limited_logger.log(f"\nAn error occurred: {e}")

url = "wss://presentation.robomaster.com/api/ws/subscriber"
asyncio.get_event_loop().run_until_complete(get_wss_data(url))

# 停止日志记录线程
log_queue.put(None)
log_thread.join()