import os
import sys

from rw import getdata
from utils import check_duplicates, guide_user_to_element, resolve_duplicates


# def get_resource_path(filename):
#     """获取资源文件路径，适用于打包后的程序"""
#     if getattr(sys, 'frozen', False):
#         # 打包后，PyInstaller 会将资源放在 _MEIPASS 目录中
#         bundle_dir = sys._MEIPASS
#     else:
#         # 开发环境中，资源文件与脚本在同一目录
#         bundle_dir = os.path.abspath(os.path.dirname(__file__))
#     return os.path.join(bundle_dir, filename)

# 生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def create_dialects_file(data):
    file_path = resource_path(os.path.join("res", "dialects.txt"))
    separator = '**separator**'

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"阳春市: [0{separator} 0{separator} 0{separator} 0{separator} 0{separator} 0]\n")

        for town, committees in data.items():
            town_prefix = f"阳春市/{town}"
            file.write(f"{town_prefix}: [0{separator} 0{separator} 0{separator} 0{separator} 0{separator} 0]\n")

            # 村民委员会
            file.write(f"{town_prefix}/村民委员会:\n")
            for committee, villages in committees['村民委员会'].items():
                committee_name = committee.replace('村民委员会', '')
                committee_prefix = f"{town_prefix}/村民委员会/{committee_name}"
                file.write(f"{committee_prefix}: [0{separator} 0{separator} 0{separator} 0{separator} 0{separator} 0]\n")

                for village in villages:
                    village_prefix = f"{committee_prefix}/{village}"
                    file.write(f"{village_prefix}: [0{separator} 0{separator} 0{separator} 0{separator} 0{separator} 0]\n")

            # 居民委员会
            file.write(f"{town_prefix}/居民委员会:\n")
            for committee in committees['居民委员会']:
                committee_prefix = f"{town_prefix}/居民委员会/{committee}"
                file.write(f"{committee_prefix}: [0{separator} 0{separator} 0{separator} 0{separator} 0{separator} 0]\n")

            # 社区
            file.write(f"{town_prefix}/社区:\n")
            for committee in committees['社区']:
                committee_prefix = f"{town_prefix}/社区/{committee}"
                file.write(f"{committee_prefix}: [0{separator} 0{separator} 0{separator} 0{separator} 0{separator} 0]\n")

    print("成功创建文件 'dialects.txt' ，并已写入初始数据。")

def query_dialects(data):
    file_path = resource_path(os.path.join("res", "dialects.txt"))
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在，请先运行功能6创建文件。")
        return

    print('*********************读取文件成功！**********************\n',
          '*****************************************************')

    dimension_names = ['方言分布', '名字由来', '人口', '注释', '维度5', '维度6']

    while True:
        element_name = input("➤请输入镇街/村寨名 (输入0退出)：")
        if element_name == "0":
            break

        duplicates = check_duplicates(data, element_name)
        if not duplicates:
            chosen_path = guide_user_to_element(data)
            if chosen_path is None:
                continue
        else:
            chosen_path = resolve_duplicates(duplicates, element_name)
            if chosen_path is None:
                continue

        if chosen_path is None:
            print(f"未找到 {element_name} 的路径")
            continue

        while True:
            if not getdata(chosen_path, file_path, dimension_names, 'r'):
                break  # 退出当前元素的维度选择，回到元素名称输入

def write_dialects(data):
    file_path = resource_path(os.path.join("res", "dialects.txt"))
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在，请先运行功能6创建文件。")
        return

    print('*********************读取文件成功！**********************\n',
          '*****************************************************')

    dimension_names = ['方言分布', '名字由来', '人口', '注释', '维度5', '维度6']

    while True:
        element_name = input("➤请输入镇街/村寨名 (输入0退出)：")
        if element_name == "0":
            break

        duplicates = check_duplicates(data, element_name)
        if not duplicates:
            chosen_path = guide_user_to_element(data)
            if chosen_path is None:
                continue
        else:
            chosen_path = resolve_duplicates(duplicates, element_name)
            if chosen_path is None:
                continue

        if chosen_path is None:
            print(f"未找到 {element_name} 的路径")
            continue

        while True:
            if not getdata(chosen_path, file_path, dimension_names, 'r+'):
                break  # 退出当前元素的维度选择，回到元素名称输入

def new_file(data, char):
    if char == 'query':
        if os.path.exists(resource_path(os.path.join("res", "dialects.txt"))):
            query_dialects(data)
        else:
            create_dialects_file(data)
            query_dialects(data)
    elif char == 'write':
        if os.path.exists(resource_path(os.path.join("res", "dialects.txt"))):
            write_dialects(data)
        else:
            print('请先运行功能6创建dialects.txt文件')
            return
    else:
        print("出现未知错误，请联系开发者")
        return
