import json
import re
from pprint import pprint

input_csv_file = '/Users/jhp/MSU/project/schooltext/data/SC/SOUTHCAROLINASchoolList.csv'
output_json_file = '/Users/jhp/MSU/project/schooltext/data/SC/SC_School.json'
column_name_list = []
documents_str = '['
with open(input_csv_file, 'r', encoding='windows-1252') as rf:
    index = 0
    for line in rf:
        temp_list = line.strip().strip('\n').split(',')
        if index == 0:
            column_name_list = temp_list
            index += 1
        else:
            # doc_str = '['
            doc_str = ''
            for idx in range(len(temp_list)):
                if idx == 0:
                    doc_str += '{'

                doc_str += '\"' + column_name_list[idx] + '\": \"' + \
                           re.sub(r'\s\s+', ' ', temp_list[idx]) + '\"'

                if idx != len(temp_list) - 1:
                    doc_str += ', '
                else:
                    doc_str += ', \"has_mission\": \"FALSE\"}'
                    # doc_str += '}'
            documents_str += doc_str + ', '
            index += 1

documents_str = documents_str[:-2] + ']'
print(documents_str)
documents_json = json.loads(documents_str)
pprint(documents_json)
with open(output_json_file, 'w', encoding='utf-8') as wf:
    json.dump(documents_json, wf, ensure_ascii=False, indent=4)
