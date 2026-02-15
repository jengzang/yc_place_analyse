import pandas as pd

# 加载Excel文件
file_path = '阳春方言.xlsx'
zibiao_total = pd.read_excel(file_path, sheet_name='字表(总)')
kouyuzi = pd.read_excel(file_path, sheet_name='口语字')

from pprint import pprint

from your_module import new_way
from your_module.data_parser import parse_village_file, convert_data_structure
from your_module.village_analysis import run_village_analysis


def output_zibiao_total_v3(matched_rows):
    """输出匹配到的"字表(总)"行，包含A到J列（去掉C列），以及K和L列的特定格式及其他指定的列"""
    columns_a_to_j = zibiao_total.columns[[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11]].tolist()  # A到J列（去掉C列）
    additional_columns = ['合水', '潭水', '河口', '分韻(1782)', '穗書']  # 其他指定的列
    selected_columns = columns_a_to_j + additional_columns
    return matched_rows[selected_columns]


def output_kouyuzi_v2(matched_rows):
    """输出匹配到的"口语字"行，去掉A G H J列"""
    selected_columns = [col for col in kouyuzi.columns if col in ['本字考', 'IPA', '粤拼', '状态', '来源', '词性', '释义', '例词例句', '注解']]
    return matched_rows[selected_columns]


def match_user_input(user_input):
    """根据用户输入进行匹配，返回匹配到的"字表(总)"和"口语字"中的行"""
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

    # Run the village analysis interactive menu
    run_village_analysis(data, converted_data)


def main():
    while True:
        print("\n输入粤拼按音查询，输入汉字按字查询\n输入0退出，输入'村庄'则进入查询阳春村庄")
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

