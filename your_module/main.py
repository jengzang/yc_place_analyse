# main.py
from pprint import pprint
import traceback

import new_way
from data_parser import parse_village_file, convert_data_structure
from village_analysis import run_village_analysis
import os
import sys


# 生成资源文件目录访问路径
def resource_path(relative_path):
    """获取资源文件的路径，无论是在开发环境还是在打包后的环境中"""
    try:
        # PyInstaller 创建一个临时文件夹，用于存放 `_MEIPASS`
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



def main():
    try:
        file_path = resource_path('res/阳春村庄名录.txt')
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(content)
        try:
            data = parse_village_file(file_path)
            converted_data = convert_data_structure(data)
        except FileNotFoundError:
            print(f"未找到文件：{file_path}\n  请检查你的exe文件目录下是否有_internal文件夹\n   如果有疑问，请咨询开发者（微信号:jengzang）")
            input("按任意键退出...")
            return
        for town, villages in data.items():
            natural_village_count = sum(len(village_list) for village_list in villages['自然村'].values())
            print(f"{town}的自然村数量: {natural_village_count}")
        print('总数量：', sum(len(villages['自然村'][committee]) for town, villages in data.items() for committee in villages['自然村']) + sum(
            len(villages[key]) for villages in data.values() for key in ['村民委员会', '居民委员会', '社区']))
        print('读取数据成功！')
        print(
            '*****************************以上为读取数据部分**************************************************************')
        print('阳春市地名查询分析          作者：杨铮      2024年6月')

        # Run the village analysis interactive menu
        run_village_analysis(data, converted_data)

    except Exception as e:
        print(f" o(╥﹏╥)o 程序出错了：\n{e}\n      请联系开发者(微信号：jengzang)")
        traceback.print_exc()
        input("\n请按任意键退出...")

if __name__ == "__main__":
    main()
