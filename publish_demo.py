import os
import json
from wechat_article import WeChatArticle

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
                    # 使用占位符URL
                    image_urls.append(f"https://mmbiz.qpic.cn/mmbiz_jpg/placeholder_{len(image_urls)+1}/")
            else:
                print(f'图片不存在: {img_path}')
                # 使用占位符URL
                image_urls.append(f"https://mmbiz.qpic.cn/mmbiz_jpg/placeholder_{len(image_urls)+1}/")
    
    # 如果没有足够的图片URL，使用占位符
    while len(image_urls) < 8:
        image_urls.append(f"https://mmbiz.qpic.cn/mmbiz_jpg/placeholder_{len(image_urls)+1}/")
    
    # 创建两列图片布局的HTML模板，使用flex布局确保图片并排显示，去除白色空区域
    html_content = f'''

    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; margin-right: 5px;">
            <img src="{image_urls[0]}" alt="图片1" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden;">
            <img src="{image_urls[1]}" alt="图片2" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; margin-right: 5px;">
            <img src="{image_urls[2]}" alt="图片3" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden;">
            <img src="{image_urls[3]}" alt="图片4" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; margin-right: 5px;">
            <img src="{image_urls[4]}" alt="图片5" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden;">
            <img src="{image_urls[5]}" alt="图片6" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; margin-right: 5px;">
            <img src="{image_urls[6]}" alt="图片7" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden;">
            <img src="{image_urls[7]}" alt="图片8" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
    </div>

    '''
    
    article_data = {
        'title': '两列图片布局示例文章',
        'author': '作者',
        'digest': '展示两列图片布局的示例文章',
        'content': html_content,
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

        # 上传封面图片（如果有）
        cover_image_path = '2.jpg'
        if os.path.exists(cover_image_path):
            print('正在检查图片...')
            from check_image import check_image
            print(check_image(cover_image_path))
            
            # 压缩图片以符合缩略图大小限制
            print('\n正在压缩图片...')
            from compress_image import compress_image
            thumb_image_path = compress_image(cover_image_path, 'thumb_2.jpg')
            
            print('\n正在上传封面图片...')
            result = wechat.upload_permanent_material(thumb_image_path, 'thumb')
            thumb_media_id = result['media_id']
            print(f'封面图片上传成功，media_id: {thumb_media_id}')
            if 'url' in result:
                print(f'图片URL: {result["url"]}')
        else:
            print('未找到封面图片，将使用默认图片')
            thumb_media_id = ''

        # 准备文章内容
        articles = create_article(wechat=wechat,image_paths=[
            'imgs/1.jpg',
            'imgs/2.jpg',
            'imgs/3.jpg',
            'imgs/4.jpg',
            'imgs/1.jpg',  # 重复使用现有图片作为示例
            'imgs/2.jpg',
            'imgs/3.jpg',
            'imgs/4.jpg',
        ])
        if thumb_media_id:
            articles[0]['thumb_media_id'] = thumb_media_id

        # 创建草稿
        print('正在创建草稿...')
        media_id = wechat.create_draft(articles)
        print(f'草稿创建成功，media_id: {media_id}')

        # 发布文章
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