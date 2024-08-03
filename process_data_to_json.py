import os
import json

def modify_json_files(directory):
    # 遍历目录下所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()  # 这里使用 strip() 移除首尾的空白字符，包括换行符
            
            # 检查文件内容是否为空
            if not content:
                continue

            # 检查是否已经加上，检测第一个字符是否为[
            if content[0] == "[":
                continue

            # 如果文件结尾是逗号，则去掉逗号
            if content[-1] == ',':
                content = content[:-1]
            
            # 添加方括号
            new_content = '[' + content + ']'
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

# 指定要处理的文件夹路径
directory_path = './data'
modify_json_files(directory_path)