import os
import shutil
from pathlib import Path

def extract_images(source_dir: str = 'imgs', target_dir: str = 'img'):
    """从源目录及其子目录提取所有图片到目标目录"""
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 支持的图片格式
    image_extensions = ('.jpg', '.jpeg', '.png')
    
    # 遍历源目录
    for root, _, files in os.walk(source_dir):
        if root == target_dir:  # 跳过目标目录
            continue
            
        for file in files:
            if file.lower().endswith(image_extensions):
                source_path = os.path.join(root, file)
                
                # 处理文件名冲突
                base_name, ext = os.path.splitext(file)
                target_path = os.path.join(target_dir, file)
                counter = 1
                
                while os.path.exists(target_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_name)
                    counter += 1
                
                # 移动文件
                try:
                    shutil.move(source_path, target_path)
                    print(f"已移动: {source_path} -> {target_path}")
                except Exception as e:
                    print(f"移动失败 {source_path}: {str(e)}")

if __name__ == '__main__':
    extract_images()
    print("处理完成！")