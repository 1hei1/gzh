import os
import json
from wechat_article import WeChatArticle
from create_cover import create_merged_cover
from check_image import check_image
from compress_image import compress_image

def load_config(config_path: str = 'config.json') -> dict:
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

        # 创建随机拼接的封面图片
        print('正在创建随机拼接封面...')
        image_dir = os.path.dirname(os.path.abspath(__file__))
        merged_cover_path = os.path.join(image_dir, 'merged_cover.jpg')
        
        # 从当前目录随机选择3张图片并拼接
        merged_cover_path = create_merged_cover(image_dir, merged_cover_path)
        print('封面图片已创建:')
        print(check_image(merged_cover_path))
        
        # 压缩图片以符合缩略图大小限制
        print('\n正在压缩封面图片...')
        thumb_image_path = compress_image(merged_cover_path, 'thumb_merged_cover.jpg')
        print(check_image(thumb_image_path))
        
        # 上传封面图片
        print('\n正在上传封面图片...')
        result = wechat.upload_permanent_material(thumb_image_path, 'thumb')
        thumb_media_id = result['media_id']
        print(f'封面图片上传成功，media_id: {thumb_media_id}')
        if 'url' in result:
            print(f'图片URL: {result["url"]}')

        # 准备文章内容
        articles = create_article()
        articles[0]['thumb_media_id'] = thumb_media_id

        # 创建草稿
        print('正在创建草稿...')
        media_id = wechat.create_draft(articles)
        print(f'草稿创建成功，media_id: {media_id}')

        # 发布文章（默认注释掉，需要时可以取消注释）
        # print('正在发布文章...')
        # publish_id = wechat.publish_draft(media_id)
        # print(f'发布任务创建成功，publish_id: {publish_id}')

        # # 等待发布完成
        # print('等待发布完成...')
        # status = wechat.wait_for_publish(publish_id)
        
        # if status['publish_status'] == 0:
        #     print('文章发布成功！')
        #     if 'article_detail' in status:
        #         for item in status['article_detail']['item']:
        #             print(f'文章链接: {item["article_url"]}')
        # else:
        #     print(f'发布失败: {status["status_desc"]}')
        #     if status.get('fail_idx'):
        #         print(f'失败的文章索引: {status["fail_idx"]}')

    except Exception as e:
        print(f'发生错误: {str(e)}')

if __name__ == '__main__':
    main()