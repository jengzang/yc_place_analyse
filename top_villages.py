from collections import Counter
from data_parser import parse_village_file


def find_top_n_villages(data, n):
    village_counter = Counter()
    village_to_location = {}

    for town, town_data in data.items():
        for committee, villages in town_data['自然村'].items():
            for village in villages:
                village_counter.update([village])
                if village not in village_to_location:
                    village_to_location[village] = []
                village_to_location[village].append((town, committee))

    most_common_villages = village_counter.most_common(n)

    print(f"出现频率前{n}高的自然村名字及其所属的镇和村民委员会：")
    for village, count in most_common_villages:
        locations = village_to_location[village]
        location_strs = [f"{town} - {committee}" for town, committee in locations]
        print(f"{village}：次数 {count}")
        for i in range(0, len(location_strs), 3):
            print("  " + "; ".join(location_strs[i:i + 3]))


# def main():
#     file_path = 'C:\\Users\\joengzaang\\PycharmProjects\\getvillagename\\阳春村庄名录.txt'
#     try:
#         data = parse_village_file(file_path)
#     except FileNotFoundError:
#         print(f"未找到文件：{file_path}")
#         return
#
#     n = int(input("请输入要查询的前n个自然村："))
#     find_top_n_villages(data, n)
#
#
# if __name__ == "__main__":
#     main()
