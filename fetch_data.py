import asyncio
import websockets
import json
import os
import time


async def get_wss_data(url):
    async with websockets.connect(url) as websocket:
        while True:
            formatted_time = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime())
            filename =  "./data/"+formatted_time+".json"
            print(filename)     #按时间启用新文件

            while True:
                try:
                    data = await websocket.recv()
                    json_str = data.decode('utf-8')
                    json_data = json.loads(json_str)            #获得数据
                    print("now")

                    try:
                        if(json_data["game"]["countdown"]==0):  #为每一局比赛开一个新文件
                            print(f'gameProgress: {json_data["game"]["progress"]}')
                            print(f'countdown: {json_data["game"]["countdown"]}')
                            print("GAME END")
                            break
                    except Exception as e:
                        print("发生错误:", e)
                    try:
                        if(json_data["game"]["progress"]!=5):  #只有进入正式比赛状态'5'才记录
                            print(f'gameProgress: {json_data["game"]["progress"]}')
                            print(f'countdown: {json_data["game"]["countdown"]}')
                            print("NOT IN A GAME")
                            print("\n")
                            continue
                    except Exception as e:
                        print("发生错误:", e)
                    else:   #将数据写入文件
                        with open(filename, 'a') as file:
                            print("writing \n")
                            json_last = json_data
                            json.dump(json_data, file, indent=4)
                            file.write(',\n')
                        file.close()
                except Exception as e:
                    print("发生错误:", e)
                finally:
                    pass

url = "wss://presentation.robomaster.com/api/ws/subscriber"
asyncio.get_event_loop().run_until_complete(get_wss_data(url))