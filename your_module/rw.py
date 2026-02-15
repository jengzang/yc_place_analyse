from utils import format_full_path
import re

def getdata(chosen_path0, file_path, dimension_names, open_mode):
    chosen_path = process_chosen_path(chosen_path0)
    if chosen_path == '阳春市':
        element_name = '阳春市'
        full_path = '阳春市'
    else:
        element_name = chosen_path[-1]
        full_path = format_full_path(chosen_path)

    has_children = len(chosen_path) <= 3
    while True:
        range_choice = '1'
        if has_children:
            if open_mode == 'r':
                print(f"请选择 {chosen_path0[-1] if chosen_path0 != '阳春市' else '阳春市'} 信息的读取范围：")
                print(f"  1: 只读取 {chosen_path0[-1]} 的具体信息")
                print(f"  2: 读取 {chosen_path0[-1]} 及其下辖的村庄信息")
            elif open_mode == 'r+':
                print(f"请选择想要修改的 {chosen_path0[-1] if chosen_path0 != '阳春市' else '阳春市'} 信息：")
                print(f"  1: 只更改 {chosen_path0[-1]} 的具体信息")
                print(f"  2: 更改 {chosen_path0[-1]} 及其下辖的全部村镇信息")
            range_choice = input("➤请输入选择的编号 (输入0退回至上一级)：")
            if range_choice not in {"0", "1", "2"}:
                print("无效的选择，请输入0、1或2。")
                continue
            if range_choice == "0":
                return False

        print("维度：")
        for i, dimension in enumerate(dimension_names, 1):
            print(f"  {i}: {dimension}", end='')
            if i % 3 == 0:
                print()
            else:
                print(' ', end='')

        dimension_input = input("➤请输入维度编号 (可以输入单个或多个数字，输入0则退至上一级)：")
        if dimension_input == "0":
            return False

        try:
            dimension_indices = [int(d) - 1 for d in dimension_input if d.isdigit()]
            if not dimension_indices or any(idx >= len(dimension_names) for idx in dimension_indices):
                raise ValueError
        except ValueError:
            print("无效的维度编号，请重新输入。")
            continue

        print('***********************************************')
        if range_choice == "1":
            find_element_in_file(chosen_path, file_path, dimension_indices, dimension_names, open_mode)
        elif range_choice == "2":
            process_with_children(chosen_path, file_path, dimension_indices, dimension_names, open_mode)
        else:
            print(f"当前模式 '{open_mode}' 不支持读取操作。")
            return False
        return True

def find_element_in_file(chosen_path, file_path, dimension_indices, dimension_names, open_mode):
    debug_path = ' -> '.join(chosen_path)
    full_path = format_full_path(chosen_path)
    print('debug - chosen_path:', chosen_path)

    if open_mode == 'r':
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        dimension_info = None
        path_str = debug_path
        for line in lines:
            line_path = line.split(':')[0].strip()
            match_result = match_line(chosen_path, line_path)
            current_path = adjust_chosen_path(line_path, chosen_path)
            if match_result:
                path_str, dimension_info = extract_and_store(line, current_path, dimension_indices, dimension_names)
                break

        if dimension_info:
            print(f"***********************************************\n{path_str} 的具体信息：")
            for k, v in dimension_info.items():
                print(f"    {k} : {v}")
            print('***********************************************')
        else:
            print(f"未找到 {debug_path} 的信息。")
    elif 'r+' in open_mode:
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

            dimension_info = None
            path_str = debug_path
            modified_lines = []
            separator = '**separator**'
            found = False

            for line in lines:
                line_path = line.split(':')[0].strip()
                line_values = line.split(':')[1].strip() if ':' in line else ""
                match_result = match_line(chosen_path, line_path)
                current_path = adjust_chosen_path(line_path, chosen_path)

                if match_result and '[' in line and ']' in line:
                    path_str, dimension_info = extract_and_store(line, current_path, [0,1,2,3,4,5], dimension_names)

                    if dimension_info:
                        print(f"\n{path_str} 的当前维度信息：")
                        for k, v in dimension_info.items():
                            print(f"    {k} : {v}")

                        for index in dimension_indices:
                            if 0 <= index < len(dimension_names):
                                dimension_to_modify = dimension_names[index]
                                if dimension_to_modify in dimension_info:
                                    current_value = dimension_info[dimension_to_modify]
                                    new_value = input(f"➤请输入 {dimension_to_modify} 的新值（当前值: {current_value}）: ").strip()
                                    if new_value:
                                        dimension_info[dimension_to_modify] = new_value
                                        print(f"已更新 {dimension_to_modify} 的值为: {new_value}")
                                    else:
                                        print(f"未输入新值，保持 {dimension_to_modify} 的当前值。")

                        new_values_list = [
                            dimension_info.get(dimension_names[i], 'N/A')
                            for i in range(len(dimension_names))
                        ]
                        new_line_values = f"[{separator.join(new_values_list)}]"
                        new_line = f"{line_path}: {new_line_values}\n"
                        line = new_line
                    found = True

                modified_lines.append(line)

                if found:
                    break

            if found:
                modified_lines.extend(lines[len(modified_lines):])

            file.seek(0)
            file.truncate()
            file.writelines(modified_lines)

        if dimension_info:
            print(f"***********************************************\n{path_str} 的修改后维度信息：")
            for k, v in dimension_info.items():
                print(f"    {k} : {v}")
            print('***********************************************')
        else:
            print(f"未找到 {debug_path} 的信息。")

def match_line(chosen_path, line_path):
    line_path_parts = line_path.split('/')
    if isinstance(chosen_path, str) and len(line_path_parts) == 1:
        return True
    elif len(line_path_parts) == len(chosen_path) + 1 or len(line_path_parts) == len(chosen_path):
        if line_path_parts[0] == chosen_path[0] and line_path_parts[1] == chosen_path[1]:
            if len(chosen_path) == 2 and len(line_path_parts) == len(chosen_path):
                return True
            elif len(chosen_path) == 2 or len(line_path_parts) == 3:
                return False
            elif line_path_parts[3] == chosen_path[2] and len(line_path_parts) == len(chosen_path) + 1:
                if len(chosen_path) == 3:
                    return True
                elif line_path_parts[4] == chosen_path[3]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

def process_with_children(chosen_path, file_path, dimension_indices, dimension_names, open_mode):
    debug_path = ' -> '.join(chosen_path)
    full_path = format_full_path(chosen_path)
    data_fromtxt = {}
    old_extra = 0
    print('debug - chosen_path:', chosen_path)

    if open_mode == 'r':
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        dimension_info = None
        path_str = debug_path
        for line in lines:
            line_path = line.split(':')[0].strip()
            match_result = match_line(chosen_path, line_path)
            current_path = adjust_chosen_path(line_path, chosen_path)
            if match_result:
                path_str, dimension_info = extract_store_print(line, current_path, dimension_indices, dimension_names)
                data_fromtxt[path_str] = dimension_info
            match_result_sub1, extra_elements, chosen_path_sub1 = match_children_line(chosen_path, line_path)
            if extra_elements != old_extra and match_result_sub1:
                print('-------------------------------------------------')
                old_extra = extra_elements

            if match_result_sub1 and (extra_elements == 1 or extra_elements == 2 or extra_elements == 3):
                current_path_sub = adjust_chosen_path(line_path, chosen_path_sub1)
                path_str, dimension_info = extract_store_print(line, current_path_sub, dimension_indices, dimension_names)
                data_fromtxt[path_str] = dimension_info
        print('*******************************************************************')

    elif open_mode == 'r+':
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

            print("选择操作模式：")
            print("1. 一键更改此地及其下辖的所有村镇的相关信息")
            print("2. 逐个更改此地及其下辖的村镇信息")
            choice = input("➤请输入操作模式 (1 或 2): ").strip()

            if choice == '1':
                new_value = input("➤请输入新的值来更新所有子级元素的指定维度: ").strip()
                for i, line in enumerate(lines):
                    line_path = line.split(':')[0].strip()
                    if '[' in line and ']' in line:
                        match_result = match_line(chosen_path, line_path)
                        current_path = adjust_chosen_path(line_path, chosen_path)

                        if match_result:
                            path_str, dimension_info = extract_store_print(line, current_path, dimension_indices, dimension_names)
                            print(f"当前行路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    print(f"将 {dimension_names[idx]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = new_value
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"

                        match_result_sub, extra_elements, chosen_path_sub = match_children_line(chosen_path, line_path)
                        if match_result_sub:
                            current_path_sub = adjust_chosen_path(line_path, chosen_path_sub)
                            path_str, dimension_info = extract_store_print(line, current_path_sub, dimension_indices, dimension_names)
                            print(f"当前子路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    print(f"将 {dimension_names[idx]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = new_value
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"

            elif choice == '2':
                for i, line in enumerate(lines):
                    line_path = line.split(':')[0].strip()
                    if '[' in line and ']' in line:
                        match_result = match_line(chosen_path, line_path)
                        current_path = adjust_chosen_path(line_path, chosen_path)

                        if match_result:
                            path_str, dimension_info = extract_store_print(line, current_path, dimension_indices, dimension_names)
                            print(f"当前行路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    new_value = input(f"➤请输入新的值来更新 {dimension_names[idx]} (输入0000退出): ").strip()
                                    if new_value == '0000':
                                        print("退出逐个更改模式")
                                        break
                                    print(f"将 {dimension_names[idx]} 从 {dimension_info[dimension_names[idx]]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = dimension_info[dimension_names[idx]]
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"

                        match_result_sub, extra_elements, chosen_path_sub = match_children_line(chosen_path, line_path)
                        if match_result_sub:
                            current_path_sub = adjust_chosen_path(line_path, chosen_path_sub)
                            path_str, dimension_info = extract_store_print(line, current_path_sub, dimension_indices, dimension_names)
                            print(f"当前子路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    new_value = input(f"➤请输入新的值来更新 {dimension_names[idx]} (输入0000退出): ").strip()
                                    if new_value == '0000':
                                        print("退出逐个更改模式")
                                        return
                                    print(f"将 {dimension_names[idx]} 从 {dimension_info[dimension_names[idx]]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = dimension_info[dimension_names[idx]]
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"

            file.seek(0)
            file.writelines(lines)
            file.truncate()

    else:
        print("不支持的文件模式。")

def extract_and_store(line, current_path, dimension_indices, dimension_names):
    start_idx = line.index('[') + 1
    end_idx = line.index(']')
    vector_data = line[start_idx:end_idx].split('**separator**')
    vector_data = [item.strip().strip("'\"") for item in vector_data]
    if isinstance(current_path, str):
        path_str = current_path
    else:
        path_str = ' -> '.join(current_path)
    return path_str, {dimension_names[i]: vector_data[i] for i in dimension_indices}

def extract_store_print(line, current_path, dimension_indices, dimension_names):
    def get_path_str(path):
        if isinstance(path, str):
            return path
        return ' -> '.join(path)

    start_idx = line.find('[') + 1
    end_idx = line.find(']')
    if start_idx == 0 or end_idx == -1:
        return None, {}
    vector_data = line[start_idx:end_idx].split('**separator**')
    vector_data = [item.strip().strip("'\"") for item in vector_data]

    path_str = get_path_str(current_path)
    dimension_info = {dimension_names[i]: vector_data[i] for i in dimension_indices}

    print(f"-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -\n{path_str} 的具体信息：")
    for k, v in dimension_info.items():
        print(f"    {k} : {v}")

    return path_str, dimension_info

def process_chosen_path(chosen_path):
    if not isinstance(chosen_path, tuple) or len(chosen_path) < 3:
        return chosen_path

    third_element = chosen_path[2]

    patterns = {
        r'(\(大队\))|(（大队）)': '',
        r'(\(居委\))|(（居委）)': '',
        r'(\(社区\))|(（社区）)': ''
    }

    for pattern, replacement in patterns.items():
        third_element = re.sub(pattern, replacement, third_element)

    new_chosen_path = (chosen_path[0], chosen_path[1], third_element) + chosen_path[3:]

    return new_chosen_path

def adjust_chosen_path(line_path, chosen_path):
    line_path_parts = line_path.split('/')
    if not isinstance(chosen_path, tuple):
        chosen_path = tuple(chosen_path)
    if isinstance(chosen_path, tuple) and len(chosen_path) >= 3 and len(line_path_parts) >= 3:
        if line_path_parts[2] == '村民委员会':
            return chosen_path[:2] + (chosen_path[2] + '(大队)',) + chosen_path[3:]
        elif line_path_parts[2] == '居民委员会':
            return chosen_path[:2] + (chosen_path[2] + '(居委)',) + chosen_path[3:]
        elif line_path_parts[2] == '社区':
            return chosen_path[:2] + (chosen_path[2] + '(社区)',) + chosen_path[3:]

    return chosen_path

def match_children_line(chosen_path, line_path):
    if isinstance(chosen_path, str):
        chosen_path = [chosen_path]
    elif not isinstance(chosen_path, (tuple, list)):
        raise ValueError("chosen_path 必须是一个字符串、元组或列表")

    line_path_parts = line_path.split('/')

    filter_keywords = ["村民委员会", "居民委员会", "社区"]
    filtered_line_path_parts = [part for part in line_path_parts if not any(keyword in part for keyword in filter_keywords)]

    match = all(part in filtered_line_path_parts for part in chosen_path)

    extra_elements_count = len(filtered_line_path_parts) - len(chosen_path)

    return match, extra_elements_count, filtered_line_path_parts
