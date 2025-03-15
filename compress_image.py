from PIL import Image
import os

def compress_image(input_path: str, output_path: str, max_size_kb: int = 2048) -> str:
    """处理图片格式

    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        max_size_kb: 最大文件大小（KB）

    Returns:
        str: 处理后的图片路径
    """
    # 打开原图
    with Image.open(input_path) as img:
        # 转换为RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 保存图片
        img.save(output_path, 'JPEG')
    
    return output_path

if __name__ == '__main__':
    try:
        input_file = '2.jpg'
        output_file = 'thumb_2.jpg'
        compressed_file = compress_image(input_file, output_file)
        print(f'图片已压缩并保存为：{compressed_file}')
    except Exception as e:
        print(f'压缩图片时出错：{str(e)}')