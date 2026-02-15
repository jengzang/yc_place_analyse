from collections import defaultdict
import re

def clean_element_name(name):
    """Remove specified substrings from the input element name if the result is more than one character."""
    cleaned_name = name.replace('镇', '').replace('街道', '').replace('村民委员会', '').replace('圩', '').replace('寨', '').replace('村', '').replace('社区', '')
    return cleaned_name if len(cleaned_name) > 1 else name

def add_suffixes(element_name):
    """Add specified substrings to the input element name."""
    suffixes = ['镇', '街道', '村民委员会', '圩', '寨', '村', '社区']
    return [element_name + suffix for suffix in suffixes]

def check_duplicates(data, element_name):
    cleaned_element_name = clean_element_name(element_name)
    suffixed_element_names = add_suffixes(element_name)

    duplicates = defaultdict(list)
    if element_name in {"阳春", "阳春市", "阳春县"}:
        duplicates[element_name].append('阳春市')
        return duplicates

    for town, committees in data.items():
        if (cleaned_element_name == town or cleaned_element_name in town or any(suffix_name in town for suffix_name in suffixed_element_names)):
            duplicates[element_name].append(('阳春市', town))

        for committee, villages in committees['村民委员会'].items():
            if (cleaned_element_name == committee or cleaned_element_name in committee or any(suffix_name in committee for suffix_name in suffixed_element_names)):
                duplicates[element_name].append(('阳春市', town, f"{committee.replace('村民委员会', '')}(大队)"))
            for village in villages:
                if (cleaned_element_name == village or cleaned_element_name in village or any(suffix_name in village for suffix_name in suffixed_element_names)):
                    duplicates[element_name].append(('阳春市', town, f"{committee.replace('村民委员会', '')}(大队)", village))

        for committee in committees['居民委员会']:
            if (cleaned_element_name == committee or cleaned_element_name in committee or any(suffix_name in committee for suffix_name in suffixed_element_names)):
                duplicates[element_name].append(('阳春市', town, f"{committee}(居委)"))

        for community in committees['社区']:
            if (cleaned_element_name == community or cleaned_element_name in community or any(suffix_name in community for suffix_name in suffixed_element_names)):
                duplicates[element_name].append(('阳春市', town, f"{community}(社区)"))

    return duplicates

def guide_user_to_element(data):
    print("未找到匹配的镇街/村寨，请逐级选择：")

    print("请选择镇或街道：")
    for i, town in enumerate(data.keys(), 1):
        print(f"  {i}: {town}", end='; ')
        if i % 5 == 0:
            print()
    print()

    while True:
        town_index0 = input("➤请输入镇或街道编号\n   注：输入带有“确定”字样将仅选择当前镇街；输入0退出：")
        if town_index0 == "0":
            return None
        try:
            town_index = int(re.search(r'\d+', town_index0).group()) - 1 if re.search(r'\d+', town_index0) else -1
            if town_index < 0 or town_index >= len(data):
                raise ValueError("无效的选择")
            break
        except ValueError:
            print("无效的选择，请重新输入。")

    selected_town = list(data.keys())[town_index]
    print(f"您选择了：{selected_town}")
    if '确定' in town_index0:
        return ['阳春市', selected_town]

    print("请选择村委会(大队)/居委会/社区：")

    village_committees = data[selected_town].get('村民委员会', [])
    resident_committees = data[selected_town].get('居民委员会', [])
    communities_committees = data[selected_town].get('社区', [])

    all_committees = []
    committee_names = []

    for name in village_committees:
        all_committees.append((name, '村民委员会'))
        committee_names.append(f"{name}(大队)")

    for name in resident_committees:
        all_committees.append((name, '居民委员会'))
        committee_names.append(f"{name}(居委会)")

    for name in communities_committees:
        all_committees.append((name, '社区'))
        committee_names.append(f"{name}(社区)")

    for i, committee in enumerate(committee_names, 1):
        display_name = committee.replace('村民委员会', '')
        print(f"  {i}: {display_name}", end='; ')
        if i % 5 == 0:
            print()
    print()

    while True:
        committee_index0 = input("➤请输入委员会编号\n    注：输入带有“确定”字样将仅选择当前村委/居委/社区；输入0退出：")
        if committee_index0 == "0":
            selected_committee = None
            break
        try:
            committee_index = int(re.search(r'\d+', committee_index0).group()) - 1 if re.search(r'\d+', committee_index0) else -1
            if committee_index < 0 or committee_index >= len(all_committees):
                raise ValueError("无效的选择")
            selected_committee, committee_type = all_committees[committee_index]
            break
        except ValueError:
            print("无效的选择，请重新输入。")

    if selected_committee is not None:
        if committee_type == '村民委员会':
            if '确定' in committee_index0:
                selected_committee_new = selected_committee.replace('村民委员会', '')
                print(f"您选择了：{selected_town} -> {selected_committee_new}")
                return ['阳春市', selected_town, selected_committee_new]

            print("请选择自然村：")
            villages = data[selected_town]['村民委员会'][selected_committee.replace('大队', '村民委员会')]
            for i, village in enumerate(villages, 1):
                print(f"  {i}: {village}", end='; ')
                if i % 5 == 0:
                    print()
            print()

            while True:
                village_index = input("➤请输入自然村编号 (输入0退出)：")
                if village_index == "0":
                    return None
                try:
                    village_index = int(village_index) - 1
                    if village_index < 0 or village_index >= len(villages):
                        raise ValueError("无效的选择")
                    break
                except ValueError:
                    print("无效的选择，请重新输入。")

            selected_village = villages[village_index]
            selected_committee_new = selected_committee.replace('村民委员会', '')
            print(f"您选择了：{selected_town} -> {selected_committee_new} -> {selected_village}")
            return ['阳春市', selected_town, selected_committee_new, selected_village]
        else:
            print(f"您选择了：{selected_town} -> {selected_committee}")
            return ['阳春市', selected_town, selected_committee]
    else:
        print("用户选择退出")

def resolve_duplicates(duplicates, element_name):
    if len(duplicates[element_name]) > 1:
        print("发现重名的镇街/村寨，请确认你的选择：")
        while True:
            for i, parents in enumerate(duplicates[element_name]):
                print(f"  {i + 1}: {' -> '.join([p for p in parents if p])}")
            choice = input("➤请输入选择的编号 (输入0退出)：")
            if choice == "0":
                return None

            try:
                choice = int(choice) - 1
                if choice < 0 or choice >= len(duplicates[element_name]):
                    raise ValueError("无效的编号")

                chosen_path = duplicates[element_name][choice]
                print(f"您选择了：{' -> '.join([p for p in chosen_path[1:] if p])}")
                return chosen_path
            except (ValueError, IndexError):
                print("输入无效，请输入有效的编号。")
    else:
        chosen_path = duplicates[element_name][0]
        if chosen_path != '阳春市':
            print(f"找到唯一匹配：{' -> '.join([p for p in chosen_path if p])}")
        else:
            print(f"找到唯一匹配：", chosen_path)
    return chosen_path

def build_full_path(data, element_name):
    def find_path(current_data, target_name, current_path):
        if isinstance(current_data, dict):
            for key, value in current_data.items():
                new_path = current_path + [key]
                if key == target_name:
                    return new_path
                result = find_path(value, target_name, new_path)
                if result:
                    return result
        elif isinstance(current_data, list):
            for item in current_data:
                result = find_path(item, target_name, current_path)
                if result:
                    return result
        return None

    for town, committees in data.items():
        path = find_path({town: committees}, element_name, [])
        if path:
            return path

    return [element_name]

def format_full_path(chosen_path):
    return ' -> '.join([p for p in chosen_path if p])

def handle_dimension_selection(chosen_path, file_path, dimension_names, mode):
    element_name = chosen_path[-1]
    full_path = format_full_path(chosen_path)

    def extract_dimensions(line_data, dimension_indices):
        return {dimension_names[i]: line_data[i] for i in dimension_indices}

    while True:
        print("请选择读取范围：")
        print("  1: 只读取当前元素的具体向量信息")
        print("  2: 读取当前元素及其所有子元素的具体向量信息")
        range_choice = input("➤请输入选择的编号 (输入0退出当前元素)：")
        if range_choice == "0":
            return False

        print("维度：")
        for i, dimension in enumerate(dimension_names, 1):
            print(f"  {i}: {dimension}")

        dimension_input = input("➤请输入维度编号 (如 '1' 或 '123'，输入0退出当前元素)：")
        if dimension_input == "0":
            return False

        dimension_indices = []
        try:
            dimension_indices = [int(d) - 1 for d in dimension_input if d.isdigit()]
        except ValueError:
            print("无效的维度编号，请重新输入。")
            continue

        if mode == 'r':
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if range_choice == "1":
                    found = False
                    for line in lines:
                        if element_name in line or element_name + '大队' in line:
                            found = True
                            line_data = eval(line.split(": ")[1])
                            dimension_info = extract_dimensions(line_data, dimension_indices)
                            print(f"{full_path} 的维度信息：{dimension_info}")
                            break
                    if not found:
                        print(f"未找到 {full_path} 的信息。")
                elif range_choice == "2":
                    found = False
                    for line in lines:
                        if any(element_name in l for l in line.split(": ")[0].split(' -> ')):
                            found = True
                            line_data = eval(line.split(": ")[1])
                            current_path = line.split(": ")[0]
                            dimension_info = extract_dimensions(line_data, dimension_indices)
                            print(f"{current_path} 的维度信息：{dimension_info}")
                    if not found:
                        print(f"未找到 {full_path} 及其子元素的信息。")

    return True

def update_children(indent_level, dimension_index, new_value, lines, start_index):
    for i in range(start_index, len(lines)):
        line = lines[i]
        current_indent = len(line) - len(line.lstrip())
        if current_indent > indent_level:
            try:
                line_data = eval(line.split(": ")[1])
                line_data[dimension_index] = new_value
                lines[i] = f"{line.split(': ')[0]}: {line_data}\n"
            except (IndexError, SyntaxError) as e:
                print(f"处理行 '{line}' 时出错：{e}")
        elif current_indent <= indent_level:
            break
