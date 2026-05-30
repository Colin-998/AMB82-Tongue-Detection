import os

file_path = 'detect.py'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 把之前加錯的參數拔掉，還原成官方原本的寫法
    content = content.replace("map_location=device, weights_only=False)", "map_location=device)")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("✅ detect.py 已經完美還原，這次真的可以測試了！")