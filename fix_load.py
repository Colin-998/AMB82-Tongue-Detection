import os

# 要修改的檔案清單 (把訓練和測試程式一次改好)
files_to_fix = ['train.py', 'detect.py']

for file_name in files_to_fix:
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尋找舊的載入指令，並加上 weights_only=False 宣告安全
        content = content.replace("map_location=device)", "map_location=device, weights_only=False)")
        
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

print("✅ 成功！PyTorch 嚴格安全性限制已解除，可以開始訓練了！")