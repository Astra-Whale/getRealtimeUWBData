import asyncio
import websockets
import json
import os
import time

class MyLogger:
    def __init__(self,rate = 10):
        self.rate = rate
        self.counter = 1
        self.last_msg_type = None

    def log(self,type,msg):
        self.counter+=1
        if self.counter % self.rate == 0 or self.last_msg_type != type:
            print(msg)
            self.counter = 1
            self.last_msg_type = type

my_logger = MyLogger(50)

async def get_wss_data(url):
    os.makedirs("./data", exist_ok=True)  # Ensure the data directory exists
    
    async with websockets.connect(url) as websocket:
        while True:
            formatted_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            filename = f"./data/{formatted_time}.json"
            # my_logger.log(filename)  # Log the new filename
            
            while True:
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    json_data = json.loads(data)  # Directly parse the received data
                    
                    if not ("game" in json_data and "countdown" in json_data["game"] and "progress" in json_data["game"]):
                        my_logger.log(1,"Required fields are missing in the JSON data")
                        continue

                    if json_data.get("game", {}).get("countdown") == 0 or json_data.get("game", {}).get("progress") != 5:  # Check if the game is going on
                        my_logger.log(2,f'gameProgress: {json_data["game"]["progress"]}\ncountdown: {json_data["game"]["countdown"]}\nNot in game\n')
                        break
                    
                    # Write data to file
                    with open(filename, 'a') as file:
                        json.dump(json_data, file, indent=4)
                        file.write(',\n')
                        my_logger.log("writing\n")
                        my_logger.log(3,f'countdown: {json_data["game"]["countdown"]}\n')
                
                except asyncio.TimeoutError:
                    my_logger.log(4,"No data received in the last 5 seconds")
                except (json.JSONDecodeError, KeyError) as e:
                    my_logger.log(5,f"Data parsing error: {e}\nJson data: {json_data}")
                except Exception as e:
                    my_logger.log(6,f"An error occurred: {e}")

url = "wss://presentation.robomaster.com/api/ws/subscriber"
asyncio.get_event_loop().run_until_complete(get_wss_data(url))
