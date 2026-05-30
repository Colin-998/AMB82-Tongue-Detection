import os

file_path = r'models/experimental.py'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解除 detect.py 載入模型時的安全鎖
    content = content.replace("torch.load(w, map_location=map_location)", "torch.load(w, map_location=map_location, weights_only=False)")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("✅ 測試安全鎖已解除，可以開始預測了！")