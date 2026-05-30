import os

yaml_content = """train: ./data/images/train
val: ./data/images/val

nc: 5
names: ['Mirror-Approximated', 'Thin-White', 'White-Greasy', 'Yellow-Greasy', 'Grey-Black']
"""

# 直接在 yolov7/data 裡面建立正確的 yaml 檔
file_path = os.path.join('.', 'data', 'tongue_v7.yaml')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(yaml_content)

print(f"✅ 成功！已在 {file_path} 建立正確的設定檔。")