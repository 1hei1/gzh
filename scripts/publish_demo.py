import os
import json
import sys

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

# 导入核心模块
from core.wechat_article import WeChatArticle
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

def create_article(wechat=None, image_paths=None):
    """创建示例文章
    
    Args:
        wechat: WeChatArticle实例，用于上传图片
        image_paths: 要上传的图片路径列表，如果为None则使用占位符URL
        
    Returns:
        list: 文章数据列表
    """
    # 创建500字的隐形文本（使用极小字体和透明颜色）
    invisible_text = "<p style='font-size:1px;color:rgba(255,255,255,0.01);'>" + "微信公众号文章模板" * 100 + "</p>"
    
    # 上传图片并获取微信图片URL
    image_urls = []
    if wechat and image_paths:
        print('正在上传文章内图片...')
        for img_path in image_paths:
            if os.path.exists(img_path):
                try:
                    url = wechat.upload_article_image(img_path)
                    image_urls.append(url)
                    print(f'图片上传成功: {url}')
                except Exception as e:
                    print(f'图片上传失败: {str(e)}')
    
    # 如果没有成功上传的图片，使用占位符
    if not image_urls:
        image_urls = [
            'https://mmbiz.qpic.cn/mmbiz_jpg/placeholder1/640?wx_fmt=jpeg',
            'https://mmbiz.qpic.cn/mmbiz_jpg/placeholder2/640?wx_fmt=jpeg'
        ]
    
    # 创建HTML内容
    content = f'''
    <p style="text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 20px;">这是一篇示例文章</p>
    <p>这是文章的正文内容，可以包含<strong>加粗</strong>、<em>斜体</em>等格式。</p>
    <p>以下是插入的图片：</p>
    <p style="text-align: center;"><img src="{image_urls[0]}" alt="示例图片1" style="max-width: 100%;"></p>
    <p>这是第二段文字，可以继续添加更多内容。</p>
    <p style="text-align: center;"><img src="{image_urls[1 % len(image_urls)]}" alt="示例图片2" style="max-width: 100%;"></p>
    <p>文章结束，感谢阅读！</p>
    {invisible_text}
    '''
    
    # 创建文章数据
    article_data = {
        'title': '这是一篇示例文章',
        'author': '作者名称',
        'digest': '这是文章摘要，会显示在文章列表中',
        'content': content,
        'content_source_url': 'https://example.com/source',
        'thumb_media_id': None,  # 初始化为None，后续会更新为实际的media_id
        'need_open_comment': 1,
        'only_fans_can_comment': 0
    }
    
    return [article_data]

def main():
    # 加载配置
    config = load_config()
    
    try:
        # 初始化公众号文章发布器
        wechat = WeChatArticle(config['appid'], config['appsecret'])
        
        # 准备封面图片
        cover_path = os.path.join(root_dir, '1.jpg')  # 使用项目根目录下的1.jpg作为封面
        if not os.path.exists(cover_path):
            print(f'封面图片不存在: {cover_path}')
            return
        
        # 检查封面图片
        print(check_image(cover_path))
        
        # 压缩封面图片
        thumb_path = os.path.join(root_dir, 'thumb_2.jpg')
        compress_image(cover_path, thumb_path, 64)  # 缩略图限制64KB
        
        # 上传封面图片
        try:
            thumb_media_id = wechat.upload_image(thumb_path, 'thumb')
            print(f'封面图片上传成功，media_id: {thumb_media_id}')
        except Exception as e:
            print(f'封面图片上传失败: {str(e)}')
            return
        
        # 准备文章内图片
        image_paths = [os.path.join(root_dir, '1.jpg'), os.path.join(root_dir, '2.jpg')]
        
        # 创建文章
        articles = create_article(wechat, image_paths)
        
        # 设置封面图片ID
        articles[0]['thumb_media_id'] = thumb_media_id
        
        # 发布文章
        result = wechat.publish_article(articles)
        print(f'文章发布成功: {result}')
        
    except Exception as e:
        print(f'发布文章时出错: {str(e)}')

if __name__ == '__main__':
    main()