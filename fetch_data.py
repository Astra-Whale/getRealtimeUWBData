import asyncio
import websockets
import json
import os
import time
from websockets.exceptions import ConnectionClosedError

def get_log_file():
    base_log_path = "./log/log"
    log_extension = ".txt"
    counter = 0

    while True:
        log_file_path = f"{base_log_path}_{counter}{log_extension}"
        if not os.path.exists(log_file_path) or os.path.getsize(log_file_path) < 10 * 1024 * 1024:
            return log_file_path
        counter += 1

class MyLogger:
    def __init__(self, rate=10):
        self.rate = rate
        self.counter = 1
        self.last_msg_type = None
        self.last_msg = None

    def log(self, type, msg):
        if self.counter % self.rate == 0 or self.last_msg_type != type or self.last_msg != msg:
            print(msg)
            log_file_path = get_log_file()
            with open(log_file_path, 'a') as file:
                file.write(msg + '\n')
            self.counter = 1
            self.last_msg_type = type
            self.last_msg = msg
        else:
            self.counter+=1


my_logger = MyLogger(50)


async def get_wss_data(url):
    os.makedirs("./data", exist_ok=True)  # Ensure the data directory exists

    while True:  # Keep trying to connect if an error occurs
        try:
            async with websockets.connect(url) as websocket:
                while True:
                    formatted_time = time.strftime(
                        "%Y-%m-%d-%H-%M-%S", time.localtime())
                    filename = f"./data/{formatted_time}.json"
                    # my_logger.log(7, filename)  # Log the new filename

                    try:
                        data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        # Directly parse the received data
                        json_data = json.loads(data)

                        if not ("game" in json_data and "countdown" in json_data["game"] and "progress" in json_data["game"]):
                            my_logger.log(
                                1, f"{formatted_time}\nRequired fields are missing in the JSON data\nJson data: {json_data}\n")
                            break

                        # Check if the game is going on
                        if json_data.get("game", {}).get("countdown") == 0 or json_data.get("game", {}).get("progress") != 5:
                            my_logger.log(
                                2, f'{formatted_time}\ngameProgress: {json_data["game"]["progress"]}\ncountdown: {json_data["game"]["countdown"]}\nNot in game\n')
                            break

                        # Write data to file
                        with open(filename, 'a') as file:
                            json.dump(json_data, file, indent=4)
                            file.write(',\n')
                            my_logger.log(
                                3, f'{formatted_time}\nwriting\ncountdown: {json_data["game"]["countdown"]}\n')

                    except asyncio.TimeoutError:
                        my_logger.log(
                            4, f"{formatted_time}\nNo data received in the last 5 seconds\n")
                    except (json.JSONDecodeError, KeyError) as e:
                        my_logger.log(
                            5, f"{formatted_time}\nData parsing error: {e}\nJson data: {json_data}\n")
                    except ConnectionClosedError as e:
                        my_logger.log(
                            6, f"{formatted_time}\nConnection closed with error: {e}\n")
                        break  # Break to handle the error and reconnect
                    except Exception as e:
                        my_logger.log(
                            7, f"{formatted_time}\nAn error occurred: {e}\n")
                        break  # Break to handle the error and reconnect

        except Exception as e:
            my_logger.log(
                8, f"{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}\nFailed to connect: {e}\n")
            await asyncio.sleep(5)  # Wait before retrying

url = "wss://presentation.robomaster.com/api/ws/subscriber"
asyncio.get_event_loop().run_until_complete(get_wss_data(url))
