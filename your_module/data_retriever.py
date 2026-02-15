def get_town_committees(data, town_name):
    matching_towns = [town for town in data if town_name in town]
    if matching_towns:
        town_name = matching_towns[0]
        committees_info = data[town_name]
        village_committees = committees_info.get('村民委员会', [])
        resident_committees = committees_info.get('居民委员会', [])
        communities = committees_info.get('社区', [])
        return village_committees, resident_committees, communities
    return [], [], []

def get_committee_villages(data, committee_name):
    for town, town_data in data.items():
        matching_committees = [committee for committee in town_data['自然村'] if committee_name in committee]
        if matching_committees:
            return town_data['自然村'][matching_committees[0]]
    return []

def get_all_villages(data, town_name=None):
    result = {}
    if town_name:
        matching_towns = [town for town in data if town_name in town]
        if matching_towns:
            town_name = matching_towns[0]
            result[town_name] = {
                '村民委员会': data[town_name].get('村民委员会', []),
                '居民委员会': data[town_name].get('居民委员会', []),
                '社区': data[town_name].get('社区', []),
                '自然村': data[town_name].get('自然村', {})
            }
    else:
        for town, town_data in data.items():
            result[town] = {
                '村民委员会': town_data.get('村民委员会', []),
                '居民委员会': town_data.get('居民委员会', []),
                '社区': town_data.get('社区', []),
                '自然村': town_data.get('自然村', {})
            }
    return result
