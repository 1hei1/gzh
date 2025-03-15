import os
from pathlib import Path
import shutil

def convert_jpeg_to_jpg(directory: str = 'img'):
    """将目录下的所有.jpeg文件转换为.jpg格式"""
    if not os.path.exists(directory):
        print(f'目录不存在: {directory}')
        return
    
    # 遍历目录下的所有文件
    for file in os.listdir(directory):
        if file.lower().endswith('.png'):
            old_path = os.path.join(directory, file)
            new_path = os.path.join(directory, file[:-5] + '.jpeg')
            
            try:
                # 如果目标文件已存在，先删除
                if os.path.exists(new_path):
                    os.remove(new_path)
                
                # 重命名文件
                shutil.move(old_path, new_path)
                print(f'已转换: {file} -> {os.path.basename(new_path)}')
            except Exception as e:
                print(f'转换失败 {file}: {str(e)}')

if __name__ == '__main__':
    convert_jpeg_to_jpg()
    print("转换完成！")