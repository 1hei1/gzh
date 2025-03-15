import os
import random
from PIL import Image
import numpy as np
from typing import List, Tuple, Optional

def create_merged_cover(image_dir: str, output_path: str, num_images: int = 3, 
                       aspect_ratio: float = 2.35, max_size_kb: int = 1024) -> str:
    """
    从指定目录随机选择图片并拼接成一张公众号封面

    Args:
        image_dir: 图片目录路径
        output_path: 输出图片路径
        num_images: 要拼接的图片数量，默认为3
        aspect_ratio: 目标宽高比，默认为2.35:1（公众号封面比例）
        max_size_kb: 最大文件大小（KB），默认1MB

    Returns:
        str: 拼接后的图片路径
    """
    # 获取目录中所有图片文件
    image_files = [f for f in os.listdir(image_dir) 
                  if os.path.isfile(os.path.join(image_dir, f)) and 
                  f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(image_files) < num_images:
        raise ValueError(f"目录中只有{len(image_files)}张图片，无法选择{num_images}张进行拼接")
    
    # 随机选择指定数量的图片
    selected_images = random.sample(image_files, num_images)
    print(f"已选择图片: {selected_images}")
    
    # 计算目标尺寸
    # 公众号封面建议尺寸为900x383（约2.35:1）
    target_width = 900
    target_height = int(target_width / aspect_ratio)
    
    # 每张图片的宽度
    single_width = target_width // num_images
    
    # 创建新图像
    merged_image = Image.new('RGB', (target_width, target_height))
    
    # 处理并拼接每张图片
    for i, img_file in enumerate(selected_images):
        img_path = os.path.join(image_dir, img_file)
        with Image.open(img_path) as img:
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整图片大小并居中裁剪
            img_ratio = img.width / img.height
            
            if img_ratio > 1:  # 宽图
                new_height = target_height
                new_width = int(new_height * img_ratio)
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                # 居中裁剪
                left = (resized_img.width - single_width) // 2
                cropped_img = resized_img.crop((left, 0, left + single_width, target_height))
            else:  # 高图
                new_width = single_width
                new_height = int(new_width / img_ratio)
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                # 居中裁剪
                top = (resized_img.height - target_height) // 2
                # 确保top不为负
                top = max(0, top)
                bottom = min(top + target_height, resized_img.height)
                cropped_img = resized_img.crop((0, top, single_width, bottom))
                # 如果裁剪后高度不足，则进行拉伸
                if cropped_img.height < target_height:
                    cropped_img = cropped_img.resize((single_width, target_height), Image.LANCZOS)
            
            # 粘贴到合并图像上
            merged_image.paste(cropped_img, (i * single_width, 0))
    
    # 保存合并后的图片
    quality = 95
    merged_image.save(output_path, 'JPEG', quality=quality)
    
    # 检查文件大小并在需要时压缩
    while os.path.getsize(output_path) / 1024 > max_size_kb and quality > 10:
        quality -= 5
        merged_image.save(output_path, 'JPEG', quality=quality)
    
    return output_path

if __name__ == '__main__':
    try:
        # 当前目录作为图片源目录
        image_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(image_dir, 'merged_cover.jpg')
        
        result = create_merged_cover(image_dir, output_file)
        print(f"封面图片已创建: {result}")
        
        # 显示图片信息
        from check_image import check_image
        print(check_image(result))
        
    except Exception as e:
        print(f"创建封面图片时出错: {str(e)}")