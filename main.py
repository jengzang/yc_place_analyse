import pandas as pd

# 加载Excel文件
file_path = '阳春方言.xlsx'
zibiao_total = pd.read_excel(file_path, sheet_name='字表(总)')
kouyuzi = pd.read_excel(file_path, sheet_name='口语字')

from pprint import pprint

import new_way
from data_parser import parse_village_file, convert_data_structure
from data_retriever import get_town_committees, get_committee_villages, get_all_villages
from data_analyzer import analyze_village_data, analyze_top_n_chars
from top_villages import find_top_n_villages
from analyze_tendencies import analyze_tendencies, print_all_debug_info


def output_zibiao_total_v3(matched_rows):
    """输出匹配到的“字表(总)”行，包含A到J列（去掉C列），以及K和L列的特定格式及其他指定的列"""
    columns_a_to_j = zibiao_total.columns[[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11]].tolist()  # A到J列（去掉C列）
    additional_columns = ['合水', '潭水', '河口', '分韻(1782)', '穗書']  # 其他指定的列
    selected_columns = columns_a_to_j + additional_columns
    return matched_rows[selected_columns]


def output_kouyuzi_v2(matched_rows):
    """输出匹配到的“口语字”行，去掉A G H J列"""
    selected_columns = [col for col in kouyuzi.columns if col in ['本字考', 'IPA', '粤拼', '状态', '来源', '词性', '释义', '例词例句', '注解']]
    return matched_rows[selected_columns]


def match_user_input(user_input):
    """根据用户输入进行匹配，返回匹配到的“字表(总)”和“口语字”中的行"""
    if all(ord(char) < 128 for char in user_input):
        # 如果输入是英文字母或数字
        match_total = zibiao_total[zibiao_total['合水'].astype(str).str.contains(user_input, na=False, case=False)]
        match_kouyuzi = kouyuzi[kouyuzi['粤拼'].astype(str).str.contains(user_input, na=False, case=False)]
    else:
        # 如果输入包含非英文字母字符
        match_total = zibiao_total[zibiao_total.iloc[:, 10].astype(str).str.contains(user_input, na=False, case=False) |
                                   zibiao_total.iloc[:, 11].astype(str).str.contains(user_input, na=False, case=False)]
        match_kouyuzi = kouyuzi[kouyuzi.iloc[:, 1].astype(str).str.contains(user_input, na=False, case=False)]
    return match_total, match_kouyuzi


def replace_newline_with_spaces(text):
    return text.replace('\n', '\n       ')


def village_project():
    file_path = '阳春村庄名录.txt'
    try:
        data = parse_village_file(file_path)
        converted_data = convert_data_structure(data)
        # pprint(converted_data)
    except FileNotFoundError:
        print(f"未找到文件：{file_path}")
        return
    for town, villages in data.items():
        natural_village_count = sum(len(village_list) for village_list in villages['自然村'].values())
        print(f"{town}的自然村数量: {natural_village_count}")
    print('总数量：', sum(len(villages['自然村'][committee]) for town, villages in data.items() for committee in
                         villages['自然村']) + sum(
        len(villages[key]) for villages in data.values() for key in ['村民委员会', '居民委员会', '社区']))
    print('读取数据成功！')
    print(
        '*****************************以上为读取数据部分**************************************************************')
    print('广东省阳春市地名分析          作者：杨铮      2024年6月')
    while True:
        print('****************************************************************************************************')
        print('  1:查询阳春市村寨名录')
        print('  2:查询某汉字或词语在阳春市自然村中的出现频次')
        print('  3:查询在阳春市自然村名字中出现次数较多的单字')
        print('  4:查询在阳春市的同名自然村')
        print('  5:分析阳春市不同镇的自然村名字的偏向性')
        print('  6:查询阳春各村信息')
        print('  7:为阳春各村添加信息')
        print('  0:退出程序')
        action = input("(*￣︶￣*)请输入数字：")

        if action == "1":
            print('1:查询阳春市村寨名录\n    若输入镇名，则输出该镇下辖的所有居、村委会信息')
            print('    若输入镇名，则输出该镇下辖的所有居、村委会信息')
            print('    若输入村委会（大队）名字，则输出该村委会（大队）下辖的所有自然村信息')
            print('    若输入镇名+全部，则输出该镇内所有的自然村信息')
            print('    若输入’全部‘二字，则输出阳春市所有的村寨名录')
            print('    输入0返回上一级')
            query = input("请输入地名：")
            print('------------------------------------------------------------------------------')
            if query == "0":
                continue

            if query == "全部":
                all_villages = get_all_villages(data)
                for town, committees in all_villages.items():
                    print(f"*{town}的村民委员会：{', '.join(committees['村民委员会'])}")
                    if committees['居民委员会']:
                        print(f"*{town}的居民委员会：{', '.join(committees['居民委员会'])}")
                    if committees['社区']:
                        print(f"*{town}的社区：{', '.join(committees['社区'])}")
                    print(f"*{town}的自然村：")
                    for committee, villages in committees['自然村'].items():
                        print(f"  ★{committee}：{', '.join(villages)}")
                    print("*******************************************************")
            elif query.endswith("全部"):
                town_name = query[:-2]
                all_villages = get_all_villages(data, town_name)
                if all_villages:
                    for town, committees in all_villages.items():
                        print(f"*{town}的村民委员会：{', '.join(committees['村民委员会'])}")
                        if committees['居民委员会']:
                            print(f"*{town}的居民委员会：{', '.join(committees['居民委员会'])}")
                        if committees['社区']:
                            print(f"*{town}的社区：{', '.join(committees['社区'])}")
                        print(f"*{town}的自然村：")
                        for committee, villages in committees['自然村'].items():
                            print(f"  ★{committee}：{', '.join(villages)}")
                else:
                    print(f"未找到与{town_name}匹配的镇或街道")
            else:
                query = query.strip("镇")  # 去掉输入的“镇”字
                # 首先进行镇的匹配
                village_committees, resident_committees, communities = get_town_committees(data, query)
                if village_committees or resident_committees or communities:
                    if village_committees:
                        print(f"村民委员会：{', '.join(village_committees)}")
                    if resident_committees:
                        print(f"居民委员会：{', '.join(resident_committees)}")
                    if communities:
                        print(f"社区：{', '.join(communities)}")
                else:
                    # 如果不是镇，进行村民委员会、居民委员会、社区的匹配
                    villages = get_committee_villages(data, query)
                    if not villages:
                        print(f"未找到与{query}匹配的镇或村民委员会/居民委员会/社区")
                        continue

                    if villages:
                        print(f"{query}的自然村：{', '.join(villages)}")

        elif action == "2":
            print('2:查询某汉字或词语在阳春市自然村中的出现频次\n    请输入一个或两个汉字')
            print('    输入0可返回上一级')
            character = input("在此输入：")
            analyze_village_data(data, character)

        elif action == "3":
            print('3:查询在阳春市自然村名字中出现次数较多的单字')
            n = int(input("查询的单字数量(输入一个数字)："))
            print(
                '是否选择查询哪些自然村名字中含有这些字？\n    输入镇或街道名字即可\n    输入“全部”查询所有镇或街道\n    输入0则退出')
            target_town = input("在此输入：")
            analyze_top_n_chars(data,n, target_town)

        elif action == "4":
            print('4:查询在阳春市的同名自然村')
            print('请输入一个数字，以决定查询多少个重名频次最高的自然村')
            print('输入0返回上一级')
            while True:
                try:
                    n = int(input("请输入要查询的前n个自然村(输入数字)："))
                    break
                except ValueError:
                    print("输入无效，请输入一个数字。")
            find_top_n_villages(data, n)

        elif action == "5":
            print('5:分析阳春市不同镇的自然村名字的偏向性\n    即某个镇的自然村取名更惯于使用或几乎不使用哪些字')
            print('  请输入分析倾向时取平均使用的镇数n：\n     注：若不了解具体原理请输入1或者2，随意输入可能会报错')
            n = int(input("在此输入："))
            target_town = input("请输入要分析的镇或街道名称（输入'全部'分析所有镇或街道）：")
            analyze_tendencies(data, n, target_town)
            print_all_debug_info()

        elif action == "6":
            print('6:查询阳春各村信息')
            print('  您可以输入任一镇街/大队/自然村的名字进行查询')
            new_way.new_file(converted_data, 'query')

        elif action == "7":
            print('7:为阳春各村添加信息')
            print('  您可以输入任一镇街/大队/自然村的名字进行添加')
            new_way.new_file(converted_data, 'write')

        elif action == "0":
            print("退出程序。")
            break

        else:
            print("无效的选择，请输入1, 2, 3, 4, 5, 6, 7或0。")


def main():
    while True:
        print("\n输入粤拼按音查询，输入汉字按字查询\n输入0退出，输入“村庄”则进入查询阳春村庄")
        user_input = input("(*￣︶￣*)请输入：")

        if user_input == "0":
            print("退出程序。")
            break
        elif user_input == "村庄":
            village_project()
            continue
        else:
            matched_total, matched_kouyuzi = match_user_input(user_input)

            # 输出匹配结果
            matched_total_output = output_zibiao_total_v3(matched_total)
            matched_kouyuzi_output = output_kouyuzi_v2(matched_kouyuzi)

            # 替换空单元格为"-"
            matched_total_output = matched_total_output.fillna('-')
            matched_kouyuzi_output = matched_kouyuzi_output.fillna('-')

            # 显示输出以供验证
            print("\n字音:")
            if not matched_total_output.empty:
                for index, row in matched_total_output.iterrows():
                    a_to_j_values = ' '.join(map(str, row.values[:9]))  # A到J列（去掉C列），以空格分隔
                    k_value = f"[{row.values[9]}"  # K列
                    l_value = f"{row.values[10]}]"  # L列
                    print(f"{a_to_j_values} {k_value},{l_value} | 合水: {row['合水']} | 潭水: {row['潭水']} | 河口: {row['河口']} | 分韵: {row['分韻(1782)']} | 广州: {row['穗書']}")
            else:
                print("No matches found.")

            print("\n口语字:")
            if not matched_kouyuzi_output.empty:
                for index, row in matched_kouyuzi_output.iterrows():
                    main_info = ' '.join(map(str, row[['本字考', 'IPA', '粤拼', '状态', '来源', '词性']].values))  # 主信息
                    shiyi = replace_newline_with_spaces(row['释义'])  # 释义
                    lici = replace_newline_with_spaces(row['例词例句'])  # 例词例句
                    zhuji = replace_newline_with_spaces(row['注解'])  # 注解
                    print(f"*****  {main_info} *****")
                    print(f"  释义: {shiyi}")
                    print(f"  示例: {lici}")
                    print(f"  注解: {zhuji}")
                    print('***************************************')
            else:
                print("No matches found.")


if __name__ == "__main__":
    main()
