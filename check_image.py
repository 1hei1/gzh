from PIL import Image
import os

def check_image(image_path):
    """检查图片的格式、大小和分辨率"""
    if not os.path.exists(image_path):
        return f'文件 {image_path} 不存在'
    
    try:
        # 获取文件大小（字节）
        file_size = os.path.getsize(image_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # 打开并检查图片
        with Image.open(image_path) as img:
            format = img.format
            mode = img.mode
            width, height = img.size
            
            result = f'''图片信息：
文件路径：{image_path}
文件大小：{file_size_mb:.2f}MB
图片格式：{format}
颜色模式：{mode}
图片尺寸：{width}x{height}'''
            
            # 检查是否符合微信要求
            issues = []
            if file_size_mb > 2:
                issues.append(f'文件大小（{file_size_mb:.2f}MB）超过2MB限制')
            if format not in ['JPEG', 'JPG', 'PNG']:
                issues.append(f'图片格式（{format}）不是JPG或PNG')
            
            if issues:
                result += '\n\n警告：\n' + '\n'.join(issues)
            
            return result
            
    except Exception as e:
        return f'检查图片时出错：{str(e)}'

if __name__ == '__main__':
    print(check_image('2.jpg'))