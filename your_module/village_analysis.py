# village_analysis.py
# Shared village analysis interactive menu logic

import new_way
from data_retriever import get_town_committees, get_committee_villages, get_all_villages
from data_analyzer import analyze_village_data, analyze_top_n_chars
from top_villages import find_top_n_villages
from analyze_tendencies import analyze_tendencies


def run_village_analysis(data, converted_data):
    """
    Run the village analysis interactive menu.

    Args:
        data: Original parsed data structure (村民委员会 as list)
        converted_data: Converted data structure (村民委员会 as dict)
    """
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
        action = input("(｡◕ˇ∀ˇ◕)请输入数字➤")

        if action == "1":
            print('1:查询阳春市村寨名录\\n    若输入镇名，则输出该镇下辖的所有居、村委会信息')
            print('    若输入镇名，则输出该镇下辖的所有居、村委会信息')
            print('    若输入村委会（大队）名字，则输出该村委会（大队）下辖的所有自然村信息')
            print('    若输入镇名+全部，则输出该镇内所有的自然村信息')
            print('    若输入"全部"二字，则输出阳春市所有的村寨名录')
            print('    输入0返回上一级')
            query = input("➤请输入地名：")
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
                query = query.strip("镇")  # 去掉输入的"镇"字
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
            print('2:查询某汉字或词语在阳春市自然村中的出现频次\\n    请输入一个或两个汉字')
            print('    输入0可返回上一级')
            character = input("➤在此输入：")
            analyze_village_data(data, character)

        elif action == "3":
            print('3:查询在阳春市自然村名字中出现次数较多的单字')
            n = int(input("➤查询的单字数量(输入一个数字)："))
            print(
                '是否选择查询哪些自然村名字中含有这些字？\\n    输入镇或街道名字即可\\n    输入"全部"查询所有镇或街道\\n    输入0则退出')
            target_town = input("➤在此输入：")
            analyze_top_n_chars(data, n, target_town)

        elif action == "4":
            print('4:查询在阳春市的同名自然村')
            print('请输入一个数字，以决定查询重名频次最高的自然村数量')
            print('   (输入0则返回上一级)')
            while True:
                try:
                    n = int(input("➤请输入要查询的前n个自然村(输入数字)："))
                    break
                except ValueError:
                    print("输入无效，请输入一个数字。")
            find_top_n_villages(data, n)

        elif action == "5":
            print('5:分析阳春市不同镇的自然村名字的偏向性\\n    (即某个镇的自然村取名更惯于使用或几乎不使用哪些字)')
            print('  请输入分析倾向时取平均使用的镇街数n：\\n     注：若不了解具体原理请输入1或者2，随意输入可能会报错')
            n = int(input("➤在此输入："))
            target_town = input("➤请输入要分析的镇或街道名称（输入'全部'分析所有镇或街道）：")
            analyze_tendencies(data, n, target_town)
            # print_all_debug_info()

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
