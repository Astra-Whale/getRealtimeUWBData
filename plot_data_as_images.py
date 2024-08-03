import json
import matplotlib.pyplot as plt

# Extract the position data from the robots with x, z coordinates, and robot ids
def pictureOneSecond(data):
    positions = []
    robot_ids = []
    for robot_id, robot_data in data['robots'].items():
        if 'comp_transform' in robot_data and 'pos' in robot_data['comp_transform']:
            if True: #robot_id != '6' and robot_id != '106':  # 排除无人机
                pos = robot_data['comp_transform']['pos']
                positions.append((pos['x'], pos['z']))
                robot_ids.append(robot_id)

    # Separate the positions into x and z lists
    x_values = [pos[0] for pos in positions]
    z_values = [-pos[1] + 5 for pos in positions]

    # Plot the positions with x and z coordinates and label with robot ids
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 15)
    ax.set_aspect('equal', adjustable='box')
    
    colors = ['red' if int(id) < 100 else 'blue' for id in robot_ids]
    ax.scatter(z_values, x_values, c=colors, marker='o')

    for i, robot_id in enumerate(robot_ids):
        ax.text(z_values[i], x_values[i], robot_id, fontsize=9, ha='right')

    ax.set_title(f'Robot Positions {420 - data["game"]["countdown"]}')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Z-axis')
    ax.grid(False)
    
    # plt.show()
    plt.savefig(f'{420 - data["game"]["countdown"]}.jpg', format='jpg', dpi=300)

# Load the JSON data
file_path = './data/2024-05-31-21-20-15.json'
with open(file_path, 'r') as file:
    list_of_json = json.load(file)

last_data = list_of_json[0]
for data in list_of_json:
    try:
        if data["game"]["countdown"]!=last_data["game"]["countdown"]:
            pictureOneSecond(data)
        last_data = data
    finally:
        pass