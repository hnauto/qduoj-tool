import tkinter as tk
import tkinter.font as tkFont
import json
import re
import os
import sys
import zipfile
import tempfile
import time
from tkinter import filedialog

from parse import parse

import shutil
from datetime import datetime



def text_to_json():
    input_text = input_box.get("1.0", tk.END)
    display_id = display_id_entry.get()
    tag_info = tag_entry.get()

    # Use regular expressions to extract information
    display_id_match = re.search(r'(\d+):', input_text) if display_id == '' else None
    title_match = re.search(r'(\d+):\s*(.*?)\n', input_text, re.DOTALL)
    description_match = re.search(r'题目描述\n(.*?)(?=\n输入)', input_text, re.DOTALL)
    input_description_match = re.search(r'输入\n(.*?)(?=\n输出)', input_text, re.DOTALL)
    output_description_match = re.search(r'输出\n(.*?)(?=\n样例输入)', input_text, re.DOTALL)
    sample_input_match = re.search(r'样例输入\n(.*?)(?=\n样例输出)', input_text, re.DOTALL)
    sample_output_match = re.search(r'样例输出\n(.*?)(?=\n提示)', input_text, re.DOTALL)
    time_limit_match = re.search(r'时间限制: (\d+)', input_text)
    memory_limit_match = re.search(r'内存限制: (\d+)', input_text)
    source_match = re.search(r'来源\n(.+?)(?=\n)', input_text)

    # Create JSON data structure
    json_data = {
        "display_id": int(display_id_match.group(1)) if display_id_match else int(display_id) if display_id else None,
        "title": title_match.group(2).strip() if title_match else None,
        "description": {
            "format": "html",
            "value": f"<p>{description_match.group(1)}</p>" if description_match else None
        },
            "tags": [
                tag_info if tag_info else "基础知识"
        ],
        "input_description": {
            "format": "html",
            "value": f"<p>{input_description_match.group(1)}</p>" if input_description_match else None
        },
        "output_description": {
            "format": "html",
            "value": f"<p>{output_description_match.group(1)}</p>" if output_description_match else None
        },
        "test_case_score": [
            {
                "score": 10,
                "input_name": "0.in",
                "output_name": "0.out"
            },
            {
                "score": 10,
                "input_name": "1.in",
                "output_name": "1.out"
            },
            {
                "score": 10,
                "input_name": "2.in",
                "output_name": "2.out"
            },
            {
                "score": 10,
                "input_name": "3.in",
                "output_name": "3.out"
            },
            {
                "score": 10,
                "input_name": "4.in",
                "output_name": "4.out"
            },
            {
                "score": 10,
                "input_name": "5.in",
                "output_name": "5.out"
            },
            {
                "score": 10,
                "input_name": "6.in",
                "output_name": "6.out"
            },
            {
                "score": 10,
                "input_name": "7.in",
                "output_name": "7.out"
            },
            {
                "score": 10,
                "input_name": "8.in",
                "output_name": "8.out"
            },
            {
                "score": 10,
                "input_name": "9.in",
                "output_name": "9.out"
            }
        ],
        "hint": {  # 添加hint字段
            "format": "html",
            "value": ""
        },
        "time_limit": 1000,
        "memory_limit": 128,
        "samples": [
            {
                "input": sample_input_match.group(1).strip() if sample_input_match else None,
                "output": sample_output_match.group(1).strip() if sample_output_match else None
            } if sample_input_match and sample_output_match else None
        ],
        "template": {},  # 保留template字段
        "spj": None,  
        "rule_type": "ACM",  # 保留rule_type字段
        "source": source_match.group(1)  if source_match else None,
        "answers": []  # 保留answers字段
    }
    # Remove any None values
    json_data_without_none = {k: v for k, v in json_data.items() if v is not None or k == "spj"}

    # Convert the JSON data to a string and display it in the JSON text widget
    json_box.delete(1.0, tk.END)
    json_box.insert(tk.END, json.dumps(json_data, indent=4, ensure_ascii=False))
    with open('problem.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


def browse_files():
    file_path = filedialog.askopenfilename(
        title="Select a ZIP file",
        initialdir="./",
        filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
    )  # 弹出文件选择对话框，只显示ZIP文件
    if file_path:  # 如果用户选择了文件
        # 将选中的文件路径插入到 input_box 输入框中
         info_label.config(text=file_path)
         if file_path:
             rename_file(file_path)


def rename_file(zip_path):
    # 定义ZIP文件所在的目录
    extract_dir = os.path.dirname(zip_path)

    # 创建testcase文件夹，如果它不存在的话
    testcase_dir = os.path.join(extract_dir, 'testcase')
    if not os.path.exists(testcase_dir):
        os.makedirs(testcase_dir)

    # 解压zip文件到当前目录
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 解压所有文件到extract_dir
        zip_ref.extractall(extract_dir)

    # 初始化最后一个test文件的编号
    last_test_number = None

    # 遍历所有文件并找到最后一个test文件的编号
    for filename in os.listdir(extract_dir):
        if filename.startswith('test') and (filename.endswith('.in') or filename.endswith('.out')):
            match = re.search(r'test(\d+)', filename)
            if match:
                number = int(match.group(1))
                if last_test_number is None or number > last_test_number:
                    last_test_number = number

    # 重命名文件夹中的文件
    for filename in os.listdir(extract_dir):
        # 从文件名中提取编号并重命名
        match = re.search(r'([a-zA-Z]+)(\d+)(.in|\.out)$', filename)
        if match:
            # 提取字母部分、编号和扩展名
            _, number, extension = match.groups()
            # 构造新的文件名，只保留数字和扩展名
            new_filename = f'{number}{extension}'
        else:
            # 如果文件名不符合预期的模式，则保持不变
            new_filename = filename
        # 重命名文件
        os.rename(os.path.join(extract_dir, filename), os.path.join(extract_dir, new_filename))

    # 检查example.in是否存在并复制
    if os.path.exists(os.path.join(extract_dir, 'sample.in')):
        shutil.copy(os.path.join(extract_dir, 'sample.in'), os.path.join(extract_dir, f'{last_test_number+1}.in'))
        shutil.copy(os.path.join(extract_dir, 'sample.out'), os.path.join(extract_dir, f'{last_test_number+1}.out')) 
    # 过滤出所有.in和.out文件
    in_out_files = [filename for filename in os.listdir(extract_dir) if filename.endswith('.in') or filename.endswith('.out')]

    # 将所有 .in 和 .out 文件移动到 testcase 文件夹
    for filename in in_out_files:
        file_path = os.path.join(extract_dir, filename)
        # 创建 testcase 文件夹，如果它不存在的话
        if not os.path.exists(testcase_dir):
            os.makedirs(testcase_dir)
        dest_file_path = os.path.join(testcase_dir, filename)
        # 移动文件
        os.rename(file_path, dest_file_path)

    # 打印重命名和移动文件的信息
    os.remove(zip_path)
    info_label.config(text=f"所有.in和.out文件已移动到 {testcase_dir} 文件夹。")
    print(f"所有.in和.out文件已移动到 {testcase_dir} 文件夹。")


def archive_files():
    # 获取 display_id，如果为空则使用默认值 "1001"
    display_id = display_id_entry.get().strip() or "1001"
    
    # 定义要打包的文件和文件夹路径
    problem_json_path = 'problem.json'
    testcase_dir = 'testcase'
    
    # 定义存档文件夹的基础名称
    base_archive_folder_name = '1'
    
    # 检查文件夹是否存在，并递增计数器直到找到一个不存在的文件夹
    folder_counter = 1
    while os.path.exists(base_archive_folder_name):
        base_archive_folder_name = f'{folder_counter}'
        folder_counter += 1
        
    # 定义存档文件夹的完整路径
    archive_folder_path = os.path.join(os.getcwd(), base_archive_folder_name)
    
    # 创建打包文件夹
    os.makedirs(archive_folder_path, exist_ok=True)
    
    # 将 problem.json 移动到打包文件夹
    shutil.move(problem_json_path, os.path.join(archive_folder_path, 'problem.json'))
    
    # 将 testcase 文件夹移动到打包文件夹
    shutil.move(testcase_dir, os.path.join(archive_folder_path, 'testcase'))

def package_folders():
    # 获取当前时间戳，格式为 YYYYMMDD-HHMMSS
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    # 创建包含时间戳的ZIP文件名
    archive_folder_name = f'QDUOJ_{timestamp}.zip'
    # 获取当前工作目录
    current_directory = os.getcwd()
    
    # 创建一个空的ZIP文件
    with zipfile.ZipFile(os.path.join(current_directory, archive_folder_name), 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历当前目录下的所有文件夹和文件
        for item in os.listdir(current_directory):
            # 检查项目是否为文件夹，并且名称以数字开头
            if os.path.isdir(os.path.join(current_directory, item)) and item.isdigit():
                # 将找到的数字文件夹添加到ZIP文件中
                # 使用 os.path.relpath 确保ZIP文件中的路径是相对于当前目录的
                # 这样可以避免在解压时创建不必要的绝对路径层级
                folder_to_archive = os.path.join(current_directory, item)
                # 将文件夹内容添加到ZIP文件中，保留原始文件夹结构
                for root, dirs, files in os.walk(folder_to_archive):
                    for file in files:
                        # 构建文件的完整路径
                        file_path = os.path.join(root, file)
                        # 计算文件相对于当前工作目录的路径
                        relative_path = os.path.relpath(file_path, current_directory)
                        # 将文件添加到ZIP文件中
                        zipf.write(file_path, arcname=relative_path)
            
            # 打印完成消息
        info_label.config(text=f"All folders have been packaged into '{archive_folder_name}'.")
def pack_files():
    # 从输入框获取 display_id，并在为空时使用默认值 "1001"
    display_id = display_id_entry.get().strip() or "1001"
    # 定义要打包的文件和文件夹路径
    problem_json_path = 'problem.json'
    testcase_dir = 'testcase'
    # 定义打包文件夹的名称
    package_folder_name = '1'
    # 定义最终的zip文件名
    zip_filename = f'{display_id}.zip'
    folder_counter = 1
    
    # 检查文件夹是否存在，并递增计数器直到找到一个不存在的文件夹
    while os.path.exists(package_folder_name):
        package_folder_name = f'{folder_counter}'
        folder_counter += 1
        
    # 定义打包文件夹的完整路径
    package_folder_path = os.path.join(os.getcwd(), package_folder_name)
    
    # 创建打包文件夹
    if not os.path.exists(package_folder_path):
        os.makedirs(package_folder_path)
    
    # 将 problem.json 复制到打包文件夹
    shutil.copy2(problem_json_path, package_folder_path)
    
    # 将 testcase 文件夹复制到打包文件夹
    testcase_new_path = os.path.join(package_folder_path, 'testcase')
    shutil.copytree(testcase_dir, testcase_new_path)
    
    # 创建一个压缩文件
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加 problem.json 到压缩文件中的 1 文件夹
        zipf.write(os.path.join(package_folder_path, 'problem.json'), arcname='1/problem.json')
        # 添加 testcase 文件夹及其内容到压缩文件中的 1 文件夹
        for root, dirs, files in os.walk(testcase_new_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算文件相对于新的 testcase 路径的相对路径
                relative_path = os.path.relpath(file_path, testcase_new_path)
                # 写入文件到压缩文件中的 1/testcase 目录
                zipf.write(file_path, arcname=f'1/testcase/{relative_path}')
        # 删除当前目录下的 problem.json 文件
    if os.path.exists(problem_json_path):
        os.remove(problem_json_path)
    
    # 删除当前目录下的 testcase 文件夹及其所有内容
    if os.path.exists(testcase_dir):
        shutil.rmtree(testcase_dir)
    
    print(f"Files packed into {zip_filename} successfully and temporary files removed.")
    info_label.config(text=f"Files packed into {zip_filename} successfully and temporary files removed.")
    



def tk_convert():
    # 将 json_data 字典保存为 problem.json 文件
    browse_files()
    text_to_json()
    archive_files()

# Create the main window
root = tk.Tk()
root.title("QindaoU OJ Convert By:Little奔")

# Configure the font for the input and JSON text widgets
font = tkFont.Font(family="Courier", size=10)

# Create the input text widget
input_box = tk.Text(root, width=50, height=30, font=font)
input_box.grid(row=1, column=0, padx=(20, 0), pady=(20, 0))

# Create the JSON text widget
json_box = tk.Text(root, width=50, height=30, font=font)
json_box.grid(row=1, column=1, padx=(10, 20), pady=(20, 20))



# Create a label for the display_id input
display_id_label = tk.Label(root, text="Display ID:")
display_id_label.grid(row=0, column=0, sticky="w", padx=(0, 0), pady=(0, 5))

# Create an input field for the display_id
display_id_entry = tk.Entry(root, width=10, font=font)
display_id_entry.grid(row=0, column=0, sticky="w", padx=(80, 10), pady=(5, 5))

# Create a label for the tag input
tag_label = tk.Label(root, text="Tag:")
tag_label.grid(row=0, column=0, sticky="w", padx=(180, 0), pady=(0, 5))

# Create an input field for the tags
tag_entry = tk.Entry(root, width=20, font=font)
tag_entry.grid(row=0, column=0, sticky="w", padx=(220, 10), pady=(5, 5))


# Create the Convert button
convert_button = tk.Button(root, text="Convert to JSON", command=tk_convert)
convert_button.grid(row=0, column=1, sticky="w", padx=(20, 10), pady=(0, 5))

# Create the Archive button
package_button = tk.Button(root, text="Package", command=package_folders)
package_button.grid(row=0, column=1, sticky="w", padx=(160, 10), pady=(0, 5))

# Create a label for the info
info_label = tk.Label(root, text="info:")
info_label.grid(row=2,column=0,sticky="w")

root.geometry("900x650")

# Start the Tkinter event loop
root.mainloop()
