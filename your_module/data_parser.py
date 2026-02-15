import re


def parse_village_file(file_path):
    data = {}
    current_town = None
    current_committee_type = None
    current_committee = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith('*****'):
                current_town = None
                current_committee_type = None
                continue
            if not current_town:
                current_town = line
                data[current_town] = {'村民委员会': [], '居民委员会': [], '社区': [], '自然村': {}}
                print(f"DEBUG: 发现镇或街道 - {current_town}")
            elif '（' in line and '）' in line and '个' in line:
                parts = line.split('（')
                committees = parts[0].split('、')
                committee_type = parts[1].split('个')[1].split('）')[0]
                current_committee_type = committee_type
                if current_committee_type not in data[current_town]:
                    data[current_town][current_committee_type] = []
                data[current_town][current_committee_type].extend(committees)
                print(f"DEBUG: 发现{committee_type} - {', '.join(committees)}，所属镇或街道 - {current_town}")
            elif line.startswith(''):
                committee_info = re.search(r'\s*(.*村民委员会)：(.*)', line)
                if committee_info:
                    current_committee = committee_info.group(1)
                    villages_raw = committee_info.group(2)
                    villages_part = re.split(r'（\d+条自然村）', villages_raw)[0]
                    villages = [v.strip() for v in re.split(r'[、及]', villages_part)]
                    if current_town and current_committee:
                        data[current_town]['自然村'][current_committee] = villages
                        print(f"DEBUG: 更新自然村 - {current_committee} 的自然村列表")
                        count_from_data = len(villages)
                        match = re.search(r'（(\d+)条自然村）', villages_raw)
                        if match:
                            count_from_brackets = int(match.group(1))
                            if count_from_data == count_from_brackets:
                                print(f"DEBUG: {current_committee} 自然村数量校验成功: {count_from_data}")
                            else:
                                print(
                                    f"ERROR: {current_committee} 自然村数量校验失败: 数据中 {count_from_data}, 括号中 {count_from_brackets}")
                        else:
                            print(
                                f"DEBUG: {current_committee} 自然村数量校验跳过，没有找到括号中的数字，数据中自然村数量: {count_from_data}")

    return data


def convert_data_structure(original_data):
    converted_data = {}
    for town, committees in original_data.items():
        if town not in converted_data:
            converted_data[town] = {
                '村民委员会': {},
                '居民委员会': committees['居民委员会'],
                '社区': committees['社区']
            }
        for committee, villages in committees['自然村'].items():
            if committee not in converted_data[town]['村民委员会']:
                converted_data[town]['村民委员会'][committee] = villages
    return converted_data