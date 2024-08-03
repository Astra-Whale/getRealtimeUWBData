import asyncio
import websockets
import json
import os
import time

async def get_wss_data(url):
    os.makedirs("./data", exist_ok=True)  # Ensure the data directory exists
    
    async with websockets.connect(url) as websocket:
        while True:
            formatted_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            filename = f"./data/{formatted_time}.json"
            print(filename)  # Log the new filename
            
            while True:
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    json_data = json.loads(data)  # Directly parse the received data
                    
                    if json_data.get("game", {}).get("countdown") == 0 or json_data.get("game", {}).get("progress") != 5:  # Check if the game is going on
                        print(f'gameProgress: {json_data["game"]["progress"]}\ncountdown: {json_data["game"]["countdown"]}\nNot in game\n')
                        break
                    
                    # Write data to file
                    with open(filename, 'a') as file:
                        json.dump(json_data, file, indent=4)
                        file.write(',\n')
                        print("writing\n")
                        print(f"countdown: {json_data["game"]["countdown"]}\n")
                
                except asyncio.TimeoutError:
                    print("No data received in the last 5 seconds")
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Data parsing error: {e}\nJson data: {json_data}")
                except Exception as e:
                    print(f"An error occurred: {e}")

url = "wss://presentation.robomaster.com/api/ws/subscriber"
asyncio.get_event_loop().run_until_complete(get_wss_data(url))
