import re
from collections import Counter

# 用于存储调试信息的全局变量
debug_info = []


def calculate_tendencies(data):
    char_town_counts = {}
    town_total_counts = Counter()
    char_total_counts = Counter()

    def filter_chars(text):
        return re.sub(r'[（）()]', '', text)

    for town, town_data in data.items():
        town_char_counter = Counter()
        for committee_name in town_data['村民委员会']:
            town_char_counter.update(filter_chars(committee_name))
        for committee_name in town_data['居民委员会']:
            town_char_counter.update(filter_chars(committee_name))
        for community_name in town_data['社区']:
            town_char_counter.update(filter_chars(community_name))
        for villages in town_data['自然村'].values():
            for village in villages:
                town_char_counter.update(filter_chars(village))

        # 计算自然村的总数
        natural_village_count = sum(len(villages) for villages in town_data['自然村'].values())
        town_total_counts[town] = natural_village_count

        for char, count in town_char_counter.items():
            if char not in char_town_counts:
                char_town_counts[char] = {}
            char_town_counts[char][town] = count
            char_total_counts[char] += count

        debug_info.append(f"镇: {town}, 字符统计: {town_char_counter}")
        debug_info.append(f"镇: {town}, 自然村总数: {town_total_counts[town]}")

    return char_town_counts, town_total_counts, char_total_counts

def analyze_tendencies(data, n, target_town=None):
    char_town_counts, town_total_counts, char_total_counts = calculate_tendencies(data)

    # 调试输出所有字符和频率
    for char, counts in char_town_counts.items():
        frequencies = {town: count / town_total_counts[town] for town, count in counts.items()}
        debug_info.append(f"'{char}': 总自然村数目: {town_total_counts}")
        debug_info.append(f"'{char}': {counts}, 频率: {frequencies}")

    if target_town and target_town != '全部':
        target_town_names = [target_town, target_town + "镇", target_town + "街道"]
        towns_to_analyze = [t for t in town_total_counts.keys() if t in target_town_names]
    else:
        towns_to_analyze = town_total_counts.keys()

    #towns_to_analyze = town_total_counts.keys()

    #if target_town:
    #  target_town_names = [target_town, target_town + "镇", target_town + "街道"]
    # towns_to_analyze = [t for t in town_total_counts.keys() if t in target_town_names]

    high_tendency_dict = {}
    low_tendency_dict = {}

    for char, counts in char_town_counts.items():
        #frequencies = {town: count / town_total_counts[town] for town, count in counts.items()}
        frequencies = {town: 0 for town in town_total_counts}
        frequencies.update({town: count / town_total_counts[town] for town, count in counts.items()})

        # 调试输出字符的频率
        debug_info.append(f"\n分析字符 '{char}' 的频率: {frequencies}")

        # 按频率排序
        sorted_towns = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
        top_towns = sorted_towns[:n]

        if top_towns:
            max_frequency = top_towns[-1][1]
            for additional_town in sorted_towns[n:]:
                if additional_town[1] == max_frequency:
                    top_towns.append(additional_town)
                else:
                    break

        bottom_towns = sorted(frequencies.items(), key=lambda x: x[1])[:n]

        if bottom_towns:
            min_frequency = bottom_towns[-1][1]
            for additional_town in sorted_towns[n:]:
                if additional_town[1] == min_frequency:
                    bottom_towns.append(additional_town)
                else:
                    break

        overall_avg = sum(frequencies[t] for t in frequencies) / len(frequencies)

        # 计算高倾向值
        print('\n', '高倾向', top_towns)
        if top_towns:
            print('\nSum of counts:', char_total_counts[char], '\n')
            if char_total_counts[char] > 10 :
                top_avg = sum(freq for _, freq in top_towns) / len(top_towns)
                high_tendency_value = (top_avg - overall_avg) / overall_avg
            else:
                high_tendency_value = 0
                top_avg = sum(freq for _, freq in top_towns) / len(top_towns)
        else:
            high_tendency_value = 0
            print('\n', '没进入高倾向循环', '\n')

        # 计算低倾向值
        print('\n', '低倾向', bottom_towns)
        if bottom_towns:
            print('\nSum of counts:', char_total_counts[char], '\n')
            if char_total_counts[char] > 20:
                bottom_avg = sum(freq for _, freq in bottom_towns) / len(bottom_towns)
                low_tendency_value = (bottom_avg - overall_avg) / overall_avg
            else:
                low_tendency_value = 0
                bottom_avg = sum(freq for _, freq in top_towns) / len(top_towns)
        else:
            low_tendency_value = 0
            print('\n', '没进入低倾向循环', '\n')

        # 调试输出倾向值计算结果
        #debug_info.append(f"字符 '{char}' 计算过程：")
        debug_info.append(
            f"'{char}'的高倾向值计算 - 顶部镇: {[t[0] for t in top_towns]}, 平均频率: {top_avg:.4f}, 总体平均频率: {overall_avg:.4f}, 高倾向值: {high_tendency_value:.4f}")
        debug_info.append(
            f"'{char}'的低倾向值计算 - 底部镇: {[t[0] for t in bottom_towns]}, 平均频率: {bottom_avg:.4f}, 总体平均频率: {overall_avg:.4f}, 低倾向值: {low_tendency_value:.4f}")

        # 记录高低倾向值到字典中
        for t, _ in top_towns:
            if t not in high_tendency_dict:
                high_tendency_dict[t] = []
            high_tendency_dict[t].append((char, high_tendency_value))

        for t, _ in bottom_towns:
            if t not in low_tendency_dict:
                low_tendency_dict[t] = []
            low_tendency_dict[t].append((char, low_tendency_value))

    # for town in towns_to_analyze:
    #     high_tendency_scores = sorted(high_tendency_dict.get(town, []), key=lambda x: x[1], reverse=True)[:10]
    #     low_tendency_scores = sorted(low_tendency_dict.get(town, []), key=lambda x: x[1])[:10]
    #
    #     debug_info.append(f"\n{town}中最高出现倾向的十个单字：")
    #     for char, value in high_tendency_scores:
    #         town_char_count = char_town_counts[char].get(town, 0)
    #         debug_info.append(
    #             f"'{char}'：倾向值 {value:.4f}，{town}出现次数：{town_char_count}，总出现次数：{char_total_counts[char]}")
    for town in towns_to_analyze:
            high_tendency_scores = sorted(high_tendency_dict.get(town, []), key=lambda x: x[1], reverse=True)
            low_tendency_scores = sorted(low_tendency_dict.get(town, []), key=lambda x: x[1])[:10]
            debug_info.append(f"\n**************回答见下******************\n{town}中最高出现倾向的十个单字：")

            # 过滤并保证输出10个字符
            valid_high_tendency_scores = []
            for char, value in high_tendency_scores:
                if len(valid_high_tendency_scores) >= 10:
                    break
                town_char_count = char_town_counts[char].get(town, 0)
                if town_char_count >= 5:
                    valid_high_tendency_scores.append((char, value))

            # 如果有效字符少于10个，从剩余的字符中补充
            if len(valid_high_tendency_scores) < 10:
                for char, value in high_tendency_scores:
                    if len(valid_high_tendency_scores) >= 10:
                        break
                    town_char_count = char_town_counts[char].get(town, 0)
                    if town_char_count < 5:
                        valid_high_tendency_scores.append((char, value))


            # 输出最终的字符和倾向值
            for char, value in valid_high_tendency_scores:
                town_char_count = char_town_counts[char].get(town, 0)
                debug_info.append(f"'{char}'：倾向值 {value:.4f}，{town}出现次数：{town_char_count}，总出现次数：{char_total_counts[char]}")

            debug_info.append(f"\n{town}中最低出现倾向的十个单字：")
            displayed_low_tendency_scores = 0
            for char, value in low_tendency_scores:
              if displayed_low_tendency_scores >= 10:
                break
              if value != 0:
                town_char_count = char_town_counts[char].get(town, 0)
                debug_info.append(
                    f"'{char}'：倾向值 {value:.4f}，{town}出现次数：{town_char_count}，总出现次数：{char_total_counts[char]}")
                displayed_low_tendency_scores += 1

            if displayed_low_tendency_scores < 10:
              debug_info.append(f"在n={n}的情况下，{town}的低倾向字不足十个")

# 新增一个函数，返回所有调试信息
def get_debug_info_for_char(target_char):
    return [info for info in debug_info if target_char in info]


# 新增一个函数，返回所有调试信息
def print_all_debug_info():
    for info in debug_info:
        print(info)
