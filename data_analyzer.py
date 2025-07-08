from collections import Counter
from data_retriever import get_town_committees, get_committee_villages, get_all_villages


def analyze_village_data(data, character):
    town_village_counts = {}
    total_count = 0
    total_entries = 0

    for town, town_data in data.items():
        count = 0
        for committee_name in town_data['村民委员会']:
            count += committee_name.count(character)
        for committee_name in town_data['居民委员会']:
            count += committee_name.count(character)
        for community_name in town_data['社区']:
            count += community_name.count(character)
        for villages in town_data['自然村'].values():
            count += sum(village.count(character) for village in villages)
        total_count_entries = (len(town_data['村民委员会']) +
                               len(town_data['居民委员会']) +
                               len(town_data['社区']) +
                               sum(len(villages) for villages in town_data['自然村'].values()))
        if count > 0:
            frequency = count / total_count_entries if total_count_entries > 0 else 0
            town_village_counts[town] = (count, frequency)
            total_count += count
            total_entries += total_count_entries

    if town_village_counts:
        print(f"字 '{character}' 在各镇的自然村中出现的次数和频率：")
        for town, (count, frequency) in town_village_counts.items():
            print(f"{town}：次数 {count}, 频率 {frequency:.4f}")
        total_num = sum(len(villages['自然村'][committee]) for town, villages in data.items() for committee in villages['自然村']) + sum(len(villages[key]) for villages in data.values() for key in ['村民委员会', '居民委员会', '社区'])
        total_frequency = total_count / total_num
        print(f"总次数：{total_count}, 总频率：{total_frequency:.4f}")

        while True:
            choice = input("请选择操作（输入镇名称输出该镇自然村，输入'全部'输出所有镇自然村，输入0返回上一级）：")
            if choice == "0":
                break
            elif choice == "全部":
                for town, town_data in data.items():
                    if town in town_village_counts:
                        print(f"{town}的自然村、村民委员会、居民委员会、社区包含字 '{character}'：")
                        matching_committees = [committee for committee in town_data['村民委员会'] if
                                               character in committee]
                        if matching_committees:
                            print(f"  村民委员会：{' '.join(matching_committees)}")
                        matching_committees = [committee for committee in town_data['居民委员会'] if
                                               character in committee]
                        if matching_committees:
                            print(f"  居民委员会：{' '.join(matching_committees)}")
                        matching_communities = [community for community in town_data['社区'] if character in community]
                        if matching_communities:
                            print(f"  社区：{' '.join(matching_communities)}")
                        for committee, villages in town_data['自然村'].items():
                            matching_villages = [village for village in villages if character in village]
                            if matching_villages:
                                print(f"  {committee}：{' '.join(matching_villages)}")
                        print("***************************************")
                break  # 自动退回上一级
            else:
                matching_towns = [town for town in town_village_counts if choice in town]
                if matching_towns:
                    for town in matching_towns:
                        town_data = data[town]
                        print(f"{town}的自然村、村民委员会、居民委员会、社区包含字 '{character}'：")
                        matching_committees = [committee for committee in town_data['村民委员会'] if
                                               character in committee]
                        if matching_committees:
                            print(f"  村民委员会：{' '.join(matching_committees)}")
                        matching_committees = [committee for committee in town_data['居民委员会'] if
                                               character in committee]
                        if matching_committees:
                            print(f"  居民委员会：{' '.join(matching_committees)}")
                        matching_communities = [community for community in town_data['社区'] if character in community]
                        if matching_communities:
                            print(f"  社区：{' '.join(matching_communities)}")
                        for committee, villages in town_data['自然村'].items():
                            matching_villages = [village for village in villages if character in village]
                            if matching_villages:
                                print(f"  {committee}：{' '.join(matching_villages)}")
                    break  # 自动退回上一级
                else:
                    print("无效的选择，请重新输入")

    else:
        print(f"未找到字 '{character}' 在任何自然村中出现")


def analyze_top_n_chars(data, n, target_town):
    char_counter = Counter()
    total_count_entries = 0

    # 尝试匹配 target_town 在 data 中的完整名称
    if target_town in data:
        full_town_name = target_town
    elif (target_town + "镇") in data:
        full_town_name = target_town + "镇"
    elif (target_town + "街道") in data:
        full_town_name = target_town + "街道"
    else:
        print(f"未找到与{target_town}匹配的镇或街道")
        return

    if full_town_name == "全部":
        for town, town_data in data.items():
            for committee_name in town_data['村民委员会']:
                char_counter.update(committee_name)
            for committee_name in town_data['居民委员会']:
                char_counter.update(committee_name)
            for community_name in town_data['社区']:
                char_counter.update(community_name)
            for villages in town_data['自然村'].values():
                for village in villages:
                    char_counter.update(village)
            total_count_entries += (len(town_data['村民委员会']) +
                                    len(town_data['居民委员会']) +
                                    len(town_data['社区']) +
                                    sum(len(villages) for villages in town_data['自然村'].values()))
    else:
        village_committees, resident_committees, communities = get_town_committees(data, full_town_name)
        if village_committees or resident_committees or communities:
            for committee_name in village_committees:
                char_counter.update(committee_name)
            for committee_name in resident_committees:
                char_counter.update(committee_name)
            for community_name in communities:
                char_counter.update(community_name)
            if full_town_name in data:
                for villages in data[full_town_name]['自然村'].values():
                    for village in villages:
                        char_counter.update(village)
                       # print(f"DEBUG: 遍历自然村 {village} 已遍历")#调试代码
                total_count_entries += (len(village_committees) +
                                        len(resident_committees) +
                                        len(communities) +
                                        sum(len(villages) for villages in data[full_town_name]['自然村'].values()))

    print(f"DEBUG: 处理镇/街道 {target_town} 时的自然村数据")
    print(f"DEBUG: 总条目数 {total_count_entries}")

    total_chars = sum(char_counter.values())
    most_common_chars = char_counter.most_common(n)

    print(f"{target_town if target_town != '全部' else '所有镇或街道'}中出现次数排行前{n}的单字及其频率：")
    for char, count in most_common_chars:
        frequency = count / total_count_entries if total_count_entries > 0 else 0
        print(f"'{char}'：次数 {count}, 频率 {frequency:.4f}")

    while True:
        ignore_choice = input("是否忽略某些字重新计算？（是/否）：")
        if ignore_choice.lower() == '是':
            ignore_chars = input("请输入要忽略的字，用空格分隔：").split()
            for char in ignore_chars:
                del char_counter[char]
            total_chars = sum(char_counter.values())
            most_common_chars = char_counter.most_common(n)
            print(
                f"忽略指定字后，{target_town if target_town != '全部' else '所有镇或街道'}中出现次数排行前{n}的单字及其频率：")
            for char, count in most_common_chars:
                frequency = count / total_count_entries if total_count_entries > 0 else 0
                print(f"'{char}'：次数 {count}, 频率 {frequency:.4f}")
        else:
            break

    display_choice = input("是否输出包含这些字的所有自然村、村民委员会、居民委员会和社区的名字？（是/否）：")
    if display_choice.lower() == '是':
        for char, count in most_common_chars:
            print(f"\n包含字 '{char}' 的自然村、村民委员会、居民委员会和社区：")
            if target_town == "全部":
                for town, town_data in data.items():
                    matching_committees = [committee for committee in town_data['村民委员会'] if char in committee]
                    if matching_committees:
                        print(f"{town} - 村民委员会：{' '.join(matching_committees)}")
                    matching_committees = [committee for committee in town_data['居民委员会'] if char in committee]
                    if matching_committees:
                        print(f"{town} - 居民委员会：{' '.join(matching_committees)}")
                    matching_communities = [community for community in town_data['社区'] if char in community]
                    if matching_communities:
                        print(f"{town} - 社区：{' '.join(matching_communities)}")
                    for committee, villages in town_data['自然村'].items():
                        matching_villages = [village for village in villages if char in village]
                        if matching_villages:
                            print(f"{town} - {committee}：{' '.join(matching_villages)}")
            else:
                    town_data = data[full_town_name]
                    matching_committees = [committee for committee in town_data['村民委员会'] if char in committee]
                    if matching_committees:
                        print(f"{full_town_name} - 村民委员会：{' '.join(matching_committees)}")
                    matching_committees = [committee for committee in town_data['居民委员会'] if char in committee]
                    if matching_committees:
                        print(f"{full_town_name} - 居民委员会：{' '.join(matching_committees)}")
                    matching_communities = [community for community in town_data['社区'] if char in '社区']
                    if matching_communities:
                        print(f"{full_town_name} - 社区：{' '.join(matching_communities)}")
                    for committee, villages in town_data['自然村'].items():
                        matching_villages = [village for village in villages if char in village]
                        if matching_villages:
                         print(f"{full_town_name} - {committee}：{' '.join(matching_villages)}")
