import os
import random
import shutil

# 設定路徑
base_dir = './data'
img_src = os.path.join(base_dir, 'images', 'JPEGImages')
lbl_src = os.path.join(base_dir, 'labels') # 假設你的txt都擠在這裡

train_img = os.path.join(base_dir, 'images', 'train')
val_img = os.path.join(base_dir, 'images', 'val')
train_lbl = os.path.join(base_dir, 'labels', 'train')
val_lbl = os.path.join(base_dir, 'labels', 'val')

# 建立正確的資料夾
for d in [train_img, val_img, train_lbl, val_lbl]:
    os.makedirs(d, exist_ok=True)

# 抓取所有圖片
if not os.path.exists(img_src):
    print("找不到 JPEGImages 資料夾，請確認路徑！")
    exit()

imgs = [f for f in os.listdir(img_src) if f.endswith(('.jpg', '.png', '.jpeg'))]
random.seed(42)
random.shuffle(imgs)

# 80%訓練，20%驗證
split = int(len(imgs) * 0.8)
train_files = imgs[:split]
val_files = imgs[split:]

def move_files(files, dest_img, dest_lbl):
    count = 0
    for img in files:
        txt = os.path.splitext(img)[0] + '.txt'
        src_i = os.path.join(img_src, img)
        src_t = os.path.join(lbl_src, txt)
        
        # 如果標籤檔存在，就一起搬家
        if os.path.exists(src_t):
            shutil.move(src_i, os.path.join(dest_img, img))
            shutil.move(src_t, os.path.join(dest_lbl, txt))
            count += 1
    return count

print("🚀 開始進行資料集切割與搬家...")
t_count = move_files(train_files, train_img, train_lbl)
v_count = move_files(val_files, val_img, val_lbl)

print(f"✅ 搞定！訓練集(train): {t_count} 張 | 驗證集(val): {v_count} 張")