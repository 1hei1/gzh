import os
import json
import sys

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

# 导入核心模块
from core.wechat_article import WeChatArticle
from core.create_cover import create_merged_cover
from core.check_image import check_image
from core.compress_image import compress_image

def load_config(config_path: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.json')) -> dict:
    """加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        dict: 配置信息
    """
    if not os.path.exists(config_path):
        config = {
            'appid': 'wx068a368be317edd0',
            'appsecret': '5a2d58d2f0c47c44c5d5fed196f7b96d'
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f'请先在{config_path}中配置公众号的appid和appsecret')
        exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_article():
    """创建示例文章"""
    article_data = {
        'title': '这是一篇使用随机拼接封面的示例文章',
        'author': '作者',
        'digest': '这是文章摘要，展示了如何使用随机拼接的图片作为封面',
        'content': '<p>这是一篇示例文章的正文内容，展示了如何使用随机拼接的图片作为微信公众号文章封面。</p>',
        'content_source_url': 'https://example.com/source',
        'thumb_media_id': None,  # 初始化为None，后续会更新为实际的media_id
        'need_open_comment': 1,
        'only_fans_can_comment': 0
    }
    # 直接返回字典列表，不进行JSON序列化和反序列化
    return [article_data]

def main():
    # 加载配置
    config = load_config()
    
    try:
        # 初始化公众号文章发布器
        wechat = WeChatArticle(config['appid'], config['appsecret'])
        
        # 准备图片目录
        img_dir = os.path.join(root_dir, 'img')
        if not os.path.exists(img_dir) or len(os.listdir(img_dir)) < 3:
            print(f'图片目录不存在或图片数量不足: {img_dir}')
            return
        
        # 创建合并封面
        merged_cover_path = os.path.join(root_dir, 'merged_cover.jpg')
        create_merged_cover(img_dir, merged_cover_path)
        
        # 检查封面图片
        print(check_image(merged_cover_path))
        
        # 压缩封面图片
        thumb_path = os.path.join(root_dir, 'thumb_merged_cover.jpg')
        compress_image(merged_cover_path, thumb_path, 64)  # 缩略图限制64KB
        
        # 上传封面图片
        try:
            thumb_media_id = wechat.upload_image(thumb_path, 'thumb')
            print(f'封面图片上传成功，media_id: {thumb_media_id}')
        except Exception as e:
            print(f'封面图片上传失败: {str(e)}')
            return
        
        # 创建文章
        articles = create_article()
        
        # 设置封面图片ID
        articles[0]['thumb_media_id'] = thumb_media_id
        
        # 发布文章
        result = wechat.publish_article(articles)
        print(f'文章发布成功: {result}')
        
    except Exception as e:
        print(f'发布文章时出错: {str(e)}')

if __name__ == '__main__':
    main()