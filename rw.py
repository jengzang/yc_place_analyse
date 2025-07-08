from utils import format_full_path
import re


def getdata(chosen_path0, file_path, dimension_names, open_mode):
    """
    处理维度选择并显示元素的维度信息。

    参数:
        chosen_path: 用户选择的元素路径
        file_path: 文件路径
        dimension_names: 维度名称列表
        open_mode: 文件操作模式 ('r' 用于读取, 'w' 用于写入)
    """
    # if chosen_path0 == '阳春市':
    #     chosen_path0 = ['阳春市']
    chosen_path = process_chosen_path(chosen_path0)
    if chosen_path == '阳春市':
        element_name = '阳春市'
        full_path = '阳春市'
    else:
        element_name = chosen_path[-1]  # 最后一个元素名
        full_path = format_full_path(chosen_path)  # 完整路径

    # 检查该元素是否有子级元素
    if len(chosen_path) <= 3:
        has_children = True
    else:
        has_children = False
    while True:
        range_choice = '1'  # 默认只读取当前元素
        if has_children:
            if open_mode == 'r':
                if chosen_path0 == '阳春市':
                    print(f"请选择阳春市信息的读取范围：")
                else:
                    print(f"请选择 {chosen_path0[-1]} 信息的读取范围：")
                print(f"  1: 只读取 {chosen_path0[-1]} 的具体信息")
                print(f"  2: 读取 {chosen_path0[-1]} 及其下辖的村庄信息")
            elif open_mode == 'r+':
                if chosen_path0 == '阳春市':
                    print(f"请选择想要修改的阳春市信息：")
                else:
                    print(f"请问您想要修改 {chosen_path0[-1]} 的哪些信息？")
                print(f"  1: 只更改 {chosen_path0[-1]} 的具体信息")
                print(f"  2: 更改 {chosen_path0[-1]} 及其下辖的全部村镇信息")
            range_choice = input("请输入选择的编号 (输入0退回至上一级)：")
            if range_choice not in {"0", "1", "2"}:
                print("无效的选择，请输入0、1或2。")
                continue
            if range_choice == "0":
                return False  # 返回 False 以指示退出到当前元素

        print("维度：")
        for i, dimension in enumerate(dimension_names, 1):
            # 打印维度，末尾不换行
            print(f"  {i}: {dimension}", end='')
            # 每三个元素换行
            if i % 3 == 0:
                print()  # 打印换行符
            else:
                print(' ', end='')  # 否则在同一行继续

        dimension_input = input("请输入维度编号 (可以输入单个或多个数字，输入0则退至上一级)：")
        if dimension_input == "0":
            return False  # 返回 False 以指示退出当前元素

        try:
            dimension_indices = [int(d) - 1 for d in dimension_input if d.isdigit()]
            if not dimension_indices or any(idx >= len(dimension_names) for idx in dimension_indices):
                raise ValueError
        except ValueError:
            print("无效的维度编号，请重新输入。")
            continue
        print('***********************************************')
        if range_choice == "1":
            print('debug: dimension_indices:', dimension_indices)
            # 只读取当前元素
            find_element_in_file(chosen_path, file_path, dimension_indices, dimension_names, open_mode)
        elif range_choice == "2":
            # 读取当前元素及其所有子元素
            process_with_children(chosen_path, file_path, dimension_indices, dimension_names, open_mode)
        else:
            print(f"当前模式 '{open_mode}' 不支持读取操作。")
            return False
        return True  # 返回 True 以指示继续


def find_element_in_file(chosen_path, file_path, dimension_indices, dimension_names, open_mode):
    debug_path = ' -> '.join(chosen_path)
    full_path = format_full_path(chosen_path)
    print('debug - chosen_path:', chosen_path)  # 调试输出路径

    if open_mode == 'r':
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        dimension_info = None
        path_str = debug_path
        for line in lines:
            line_path = line.split(':')[0].strip()
            match_result = match_line(chosen_path, line_path)
            # print('debug - line_path:', line_path, match_result)  # 调试输出每行的路径
            current_path = adjust_chosen_path(line_path, chosen_path)
            if match_result:
                path_str, dimension_info = extract_and_store(line, current_path, dimension_indices,
                                                             dimension_names)
                # print('debug - path_str:', path_str)
                break

        if dimension_info:
            print(f"***********************************************\n{path_str} 的具体信息：")
            for k, v in dimension_info.items():
                print(f"    {k} : {v}")
            print('***********************************************')
        else:
            print(f"未找到 {debug_path} 的信息。")
    elif 'r+' in open_mode:
        # 读取文件内容
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

            dimension_info = None
            path_str = debug_path
            modified_lines = []
            separator = '**separator**'
            found = False
            # print("debug - 正在处理文件行...")

            for line in lines:
                line_path = line.split(':')[0].strip()
                line_values = line.split(':')[1].strip() if ':' in line else ""
                match_result = match_line(chosen_path, line_path)
                # print(f"debug - 处理行: {line.strip()}")
                # print(f"debug - line_path: {line_path}, match_result: {match_result}")
                current_path = adjust_chosen_path(line_path, chosen_path)

                # 检查行中是否包含 []
                if match_result and '[' in line and ']' in line:
                    print(f"debug - 匹配成功并包含括号: {line.strip()}")
                    # 调用 extract_and_store 提取维度信息
                    path_str, dimension_info = extract_and_store(line, current_path, [0,1,2,3,4,5], dimension_names)
                    print(f"debug - 提取的 dimension_info: {dimension_info}")

                    if dimension_info:
                        # 显示当前维度信息
                        print(f"\n{path_str} 的当前维度信息：")
                        for k, v in dimension_info.items():
                            print(f"    {k} : {v}")
                        # print('debug dimension_indices:', dimension_indices)
                        # print('debug dimension_info:', dimension_info)

                        # 修改维度信息
                        for index in dimension_indices:
                            if 0 <= index < len(dimension_names):  # 索引有效性检查
                                dimension_to_modify = dimension_names[index]
                                if dimension_to_modify in dimension_info:
                                    current_value = dimension_info[dimension_to_modify]
                                    # print('debug current_value:', current_value)
                                    # print('debug dimensiontomodify:', dimension_to_modify)
                                    # print('debug ')
                                    new_value = input(
                                        f"请输入 {dimension_to_modify} 的新值（当前值: {current_value}）: ").strip()
                                    if new_value:
                                        dimension_info[dimension_to_modify] = new_value
                                        print(f"debug - 已更新 {dimension_to_modify} 的值为: {new_value}")
                                    else:
                                        print(f"debug - 未输入新值，保持 {dimension_to_modify} 的当前值。")
                                else:
                                    print(f"debug - {dimension_to_modify} 当前没有值，跳过修改。")
                            else:
                                print(f"debug - 无效的索引: {index}")
                        # print('debug dimension_info:', dimension_info)
                        # 更新行数据
                        new_values_list = [
                            dimension_info.get(dimension_names[i], 'N/A')  # 使用 'N/A' 作为后备，但确保信息已经更新
                            for i in range(len(dimension_names))
                        ]
                        # print('debug: new_value_list', new_values_list)
                        new_line_values = f"[{separator.join(new_values_list)}]"
                        new_line = f"{line_path}: {new_line_values}\n"
                        line = new_line
                        print(line)

                        # 标记为找到目标行
                    found = True

                modified_lines.append(line)

                # 如果找到匹配行则停止查找
                if found:
                    break

            # 添加后续未修改的行
            if found:
                modified_lines.extend(lines[len(modified_lines):])

            # 清空文件并写入修改后的内容
            file.seek(0)
            file.truncate()
            file.writelines(modified_lines)

        # 输出修改后的结果
        if dimension_info:
            print(f"***********************************************\n{path_str} 的修改后维度信息：")
            for k, v in dimension_info.items():
                print(f"    {k} : {v}")
            print('***********************************************')
        else:
            print(f"未找到 {debug_path} 的信息。")


def match_line(chosen_path, line_path):
    """
    根据 chosen_path 的元素逐级匹配 line_path 的相应部分。

    参数:
        chosen_path: 用户选择的路径 (元组或列表)
        line_path: 文件中的路径 (字符串)

    返回:
        布尔值，表示 chosen_path 是否与 line_path 匹配
    """
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
    """
    处理当前元素及其所有子元素的维度信息，并从文件中读取或写入行内容。

    参数:
        chosen_path: 用户选择的元素路径
        file_path: 文件路径
        dimension_indices: 用户选择的维度索引
        dimension_names: 维度名称列表
        open_mode: 文件操作模式 ('r' 用于读取, 'w' 用于写入)
    """
    debug_path = ' -> '.join(chosen_path)
    full_path = format_full_path(chosen_path)
    data_fromtxt = {}
    old_extra = 0
    print('debug - chosen_path:', chosen_path)  # 调试输出路径

    if open_mode == 'r':
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        dimension_info = None
        path_str = debug_path
        for line in lines:
            line_path = line.split(':')[0].strip()
            match_result = match_line(chosen_path, line_path)
            # print('debug - line_path:', line_path, match_result)  # 调试输出每行的路径
            current_path = adjust_chosen_path(line_path, chosen_path)
            if match_result:
                path_str, dimension_info = extract_store_print(line, current_path, dimension_indices,
                                                               dimension_names)
                data_fromtxt[path_str] = dimension_info
                # print('debug - path_str:', path_str)
            match_result_sub1, extra_elements, chosen_path_sub1 = match_children_line(chosen_path, line_path)
            # print('1debug - line_path:', line_path, match_result_sub1, extra_elements)  # 调试输出每行的路径
            if extra_elements != old_extra and match_result_sub1:
                print('-------------------------------------------------')
                old_extra = extra_elements

            if match_result_sub1 and (extra_elements == 1 or extra_elements == 2 or extra_elements == 3):
                current_path_sub = adjust_chosen_path(line_path, chosen_path_sub1)
                # print('debug:current_path_sub', current_path_sub)
                # print('debug:chosen_path_sub1', chosen_path_sub1)
                # print('debug:is', isinstance(chosen_path_sub1, tuple))
                path_str, dimension_info = extract_store_print(line, current_path_sub, dimension_indices,
                                                               dimension_names)
                data_fromtxt[path_str] = dimension_info
        print('*******************************************************************')
        # if data_fromtxt:
        #     print(f"***********************************************\n{path_str} 的具体信息：")
        #     for k, v in data_fromtxt.items():
        #         print(f"    {k} : {v}")
        #     print('***********************************************')
        # else:
        #     print(f"未找到 {debug_path} 的信息。")


    elif open_mode == 'r+':
        # 读写模式
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

            print("选择操作模式：")
            print("1. 一键更改此地及其下辖的所有村镇的相关信息")
            print("2. 逐个更改此地及其下辖的村镇信息")
            choice = input("请输入操作模式 (1 或 2): ").strip()

            if choice == '1':
                # 一键更改模式
                new_value = input("请输入新的值来更新所有子级元素的指定维度: ").strip()
                for i, line in enumerate(lines):
                    line_path = line.split(':')[0].strip()
                    if '[' in line and ']' in line:
                        match_result = match_line(chosen_path, line_path)  # 匹配行路径
                        current_path = adjust_chosen_path(line_path, chosen_path)  # 调整路径

                        if match_result:
                            path_str, dimension_info = extract_store_print(line, current_path, dimension_indices, dimension_names)
                            print(f"当前行路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    print(f"将 {dimension_names[idx]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value  # 更新为新值
                                # else:
                                #     print(f"警告: {dimension_names[idx]} 不存在于维度信息中。")
                            # 更新向量数据
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = new_value  # 更新向量数据
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"

                        match_result_sub, extra_elements, chosen_path_sub = match_children_line(chosen_path, line_path)  # 匹配子路径
                        if match_result_sub:
                            current_path_sub = adjust_chosen_path(line_path, chosen_path_sub)
                            path_str, dimension_info = extract_store_print(line, current_path_sub, dimension_indices, dimension_names)
                            print(f"当前子路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    print(f"将 {dimension_names[idx]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value  # 更新为新值
                                # else:
                                    # print(f"警告: {dimension_names[idx]} 不存在于维度信息中。")
                            # 更新向量数据
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = new_value  # 更新向量数据
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"
                    # else:
                        # print(f"警告: 行 {line_path} 不包含向量数据。")

            elif choice == '2':
                # 逐个更改模式
                for i, line in enumerate(lines):
                    line_path = line.split(':')[0].strip()
                    if '[' in line and ']' in line:
                        match_result = match_line(chosen_path, line_path)  # 匹配行路径
                        current_path = adjust_chosen_path(line_path, chosen_path)  # 调整路径

                        if match_result:
                            # 提取当前行的向量信息
                            path_str, dimension_info = extract_store_print(line, current_path, dimension_indices, dimension_names)
                            print(f"当前行路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    new_value = input(f"请输入新的值来更新 {dimension_names[idx]} (输入0000退出): ").strip()
                                    if new_value == '0000':
                                        print("退出逐个更改模式")
                                        break  # 用户输入0000，退出循环
                                    print(f"将 {dimension_names[idx]} 从 {dimension_info[dimension_names[idx]]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value  # 更新维度信息
                                # else:
                                    # print(f"警告: {dimension_names[idx]} 不存在于维度信息中。")
                            # 更新向量数据
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = dimension_info[dimension_names[idx]]
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"

                        match_result_sub, extra_elements, chosen_path_sub = match_children_line(chosen_path, line_path)  # 匹配子路径
                        if match_result_sub:
                            current_path_sub = adjust_chosen_path(line_path, chosen_path_sub)  # 调整子路径
                            # 提取子路径行的向量信息
                            path_str, dimension_info = extract_store_print(line, current_path_sub, dimension_indices, dimension_names)
                            print(f"当前子路径: {path_str}")
                            for idx in dimension_indices:
                                if dimension_names[idx] in dimension_info:
                                    print(f"当前 {dimension_names[idx]}: {dimension_info[dimension_names[idx]]}")
                                    new_value = input(f"请输入新的值来更新 {dimension_names[idx]} (输入0000退出): ").strip()
                                    if new_value == '0000':
                                        print("退出逐个更改模式")
                                        return  # 用户输入0000，退出循环
                                    print(f"将 {dimension_names[idx]} 从 {dimension_info[dimension_names[idx]]} 更新为: {new_value}")
                                    dimension_info[dimension_names[idx]] = new_value  # 更新维度信息
                                # else:
                                    # print(f"警告: {dimension_names[idx]} 不存在于维度信息中。")
                            # 更新向量数据
                            start_idx = line.index('[') + 1
                            end_idx = line.index(']')
                            vector_data = line[start_idx:end_idx].split('**separator**')
                            for idx in dimension_indices:
                                if idx < len(vector_data):
                                    vector_data[idx] = dimension_info[dimension_names[idx]]
                            lines[i] = f"{line_path}: [{'**separator**'.join(vector_data)}]\n"
                    # else:
                    #     print(f"警告: 行 {line_path} 不包含向量数据。")

            file.seek(0)
            file.writelines(lines)  # 写入修改后的内容
            file.truncate()  # 截断文件，防止内容溢出


    else:
        print("不支持的文件模式。")


def extract_and_store(line, current_path, dimension_indices, dimension_names):
    """
    从行数据中提取向量信息并存储到字典中。

    参数:
        line: 当前处理的行 (字符串)
        current_path: 当前路径层级 (列表)
        dimension_indices: 用户选择的维度索引 (列表)
        dimension_names: 维度名称列表 (列表)

    返回:
        包含所选维度信息的字典条目
    """
    start_idx = line.index('[') + 1
    end_idx = line.index(']')
    vector_data = line[start_idx:end_idx].split('**separator**')
    vector_data = [item.strip().strip("'\"") for item in vector_data]
    # print('debug', current_path)
    if isinstance(current_path, str):
        path_str = current_path
    else:
        path_str = ' -> '.join(current_path)
    # print('debuggggg', path_str)
    return path_str, {dimension_names[i]: vector_data[i] for i in dimension_indices}


def extract_store_print(line, current_path, dimension_indices, dimension_names):
    """
    从行数据中提取向量信息并存储到字典中，并输出信息。

    参数:
        line: 当前处理的行 (字符串)
        current_path: 当前路径层级 (列表或字符串)
        dimension_indices: 用户选择的维度索引 (列表)
        dimension_names: 维度名称列表 (列表)

    实现：读取与输出该行的数据

    返回:
        包含所选维度信息的路径字符串和字典条目
    """

    def get_path_str(path):
        """
        处理路径信息，返回路径字符串。
        """
        if isinstance(path, str):
            return path
        return ' -> '.join(path)

    # 提取方括号中的内容
    start_idx = line.find('[') + 1
    end_idx = line.find(']')
    if start_idx == 0 or end_idx == -1:
        # print(f"Warning: Line does not contain valid brackets: {line}")
        return None, {}
    vector_data = line[start_idx:end_idx].split('**separator**')
    vector_data = [item.strip().strip("'\"") for item in vector_data]

    # Debug 信息
    # print(f"vector_data: {vector_data}")
    # print(f"vector_data length: {len(vector_data)}")
    # print(f"dimension_indices: {dimension_indices}")

    path_str = get_path_str(current_path)
    dimension_info = {dimension_names[i]: vector_data[i] for i in dimension_indices}

    # 输出信息
    print(f"-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -\n{path_str} 的具体信息：")
    for k, v in dimension_info.items():
        print(f"    {k} : {v}")
    # print('-----------------------------------------------')

    return path_str, dimension_info


def process_chosen_path(chosen_path):
    """
    处理选择的路径，将符合条件的第三个元素进行正则替换。

    参数:
        chosen_path: 用户选择的元素路径 (元组)

    返回:
        处理后的路径 (元组)
    """
    # 确保输入是元组且有至少三个元素
    if not isinstance(chosen_path, tuple) or len(chosen_path) < 3:
        return chosen_path

    third_element = chosen_path[2]

    # 定义处理后缀的正则表达式模式
    patterns = {
        r'(\(大队\))|(（大队）)': '',
        r'(\(居委\))|(（居委）)': '',
        r'(\(社区\))|(（社区）)': ''
    }

    # 使用正则表达式处理第三个元素
    for pattern, replacement in patterns.items():
        third_element = re.sub(pattern, replacement, third_element)

    # 创建新的元组
    new_chosen_path = (chosen_path[0], chosen_path[1], third_element) + chosen_path[3:]

    return new_chosen_path


def adjust_chosen_path(line_path, chosen_path):
    """
    根据 line_path 的第三部分，调整 chosen_path 的第三个元素，附加适当的后缀。

    参数:
        line_path: 行路径字符串，用于提取路径部分（字符串）。
        chosen_path: 被选择的路径（元组）。

    返回:
        调整后的路径（元组）。
    """
    # 分割 line_path 获取各部分
    line_path_parts = line_path.split('/')
    # 确保 chosen_path 是一个长度至少为 3 的元组
    if not isinstance(chosen_path, tuple):
        chosen_path = tuple(chosen_path)
    if isinstance(chosen_path, tuple) and len(chosen_path) >= 3 and len(line_path_parts) >= 3:
        # print('debug:line_path_parts[2]', line_path_parts[2])
        if line_path_parts[2] == '村民委员会':
            return chosen_path[:2] + (chosen_path[2] + '(大队)',) + chosen_path[3:]
        elif line_path_parts[2] == '居民委员会':
            return chosen_path[:2] + (chosen_path[2] + '(居委)',) + chosen_path[3:]
        elif line_path_parts[2] == '社区':
            return chosen_path[:2] + (chosen_path[2] + '(社区)',) + chosen_path[3:]

    # 如果条件不满足，返回原路径
    return chosen_path


def match_children_line(chosen_path, line_path):
    """
    检查 chosen_path 的所有部分是否都存在于 line_path 中，并返回匹配结果、
    过滤掉关键字后的 line_path 比 chosen_path 多出的元素数以及过滤后的路径列表。

    参数:
        chosen_path (str, tuple, list): 被选择的路径。
        line_path (str): 行路径字符串。

    返回:
        bool: 是否匹配。
        int: 过滤后的 line_path 比 chosen_path 多出的元素数。
        list: 过滤后的 line_path 元素列表。
    """
    # 确保 chosen_path 处理为一个列表
    if isinstance(chosen_path, str):
        chosen_path = [chosen_path]
    elif not isinstance(chosen_path, (tuple, list)):
        raise ValueError("chosen_path 必须是一个字符串、元组或列表")

    line_path_parts = line_path.split('/')

    # 过滤 line_path 中的元素
    filter_keywords = ["村民委员会", "居民委员会", "社区"]
    filtered_line_path_parts = [part for part in line_path_parts if
                                not any(keyword in part for keyword in filter_keywords)]

    # 检查 chosen_path 的所有部分是否存在于过滤后的 line_path 中
    match = all(part in filtered_line_path_parts for part in chosen_path)

    # 计算过滤后的 line_path 比 chosen_path 多出的元素数
    extra_elements_count = len(filtered_line_path_parts) - len(chosen_path)

    return match, extra_elements_count, filtered_line_path_parts
