import os
import json
import random
from wechat_article import WeChatArticle
from create_cover import create_merged_cover
from check_image import check_image
from compress_image import compress_image

def load_config(config_path: str = 'config.json') -> dict:
    """加载配置文件"""
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

def get_unprocessed_directory(config: dict) -> str:
    """获取一个未处理过的目录
    
    Args:
        config: 配置信息字典
        
    Returns:
        str: 未处理的目录路径，如果所有目录都已处理则返回None
    """
    base_dir = config.get('image_base_dir', 'imgs')  # 从配置中获取图库根目录，默认为'imgs'
    # 加载已处理的目录列表
    processed_dirs_file = 'processed_dirs.json'
    try:
        with open(processed_dirs_file, 'r', encoding='utf-8') as f:
            processed_dirs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        processed_dirs = []
    
    # 获取所有子目录
    all_dirs = []
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            
                dir_path = os.path.join(root, d)
                all_dirs.append(dir_path)
    
    # 找出未处理的目录
    unprocessed_dirs = [d for d in all_dirs if d not in processed_dirs]
    
    if not unprocessed_dirs:
        print('所有目录都已处理完毕')
        return None
    
    # 随机选择一个未处理的目录
    selected_dir = random.choice(unprocessed_dirs)
    
    # 更新已处理目录列表
    processed_dirs.append(selected_dir)
    with open(processed_dirs_file, 'w', encoding='utf-8') as f:
        json.dump(processed_dirs, f, indent=4, ensure_ascii=False)
    
    return selected_dir

def get_random_images(folder: str, count: int = None) -> list:
    """从指定文件夹及其子目录随机选择图片，确保选择的图片具有相似的宽高比
    
    Args:
        folder: 根目录路径
        count: 需要的图片数量，如果为None则返回所有图片
        
    Returns:
        list: 图片路径列表
    """
    if not os.path.exists(folder):
        print(f'文件夹不存在: {folder}')
        return []
    
    from PIL import Image
    
    # 存储图片信息的列表，每个元素为(文件路径, 宽高比)
    image_info = []
    
    # 递归遍历目录
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    img_path = os.path.join(root, f)
                    with Image.open(img_path) as img:
                        ratio = img.width / img.height
                        image_info.append((img_path, ratio))
                except Exception as e:
                    print(f'读取图片失败: {f}, 错误: {str(e)}')
    
    if not image_info:
        print(f'目录中没有有效图片: {folder}')
        return []
    
    # 按宽高比排序
    image_info.sort(key=lambda x: x[1])
    
    # 如果未指定数量或图片数量不足，返回所有图片
    if count is None or len(image_info) <= count:
        paths = [path for path, _ in image_info]
        # 如果指定了数量，确保返回偶数数量的图片
        if count is not None and len(paths) % 2 != 0:
            paths = paths[:-1]  # 移除最后一张图片以确保偶数
        return paths
    
    # 确保请求的数量为偶数
    if count % 2 != 0:
        count -= 1
    
    # 尝试找到宽高比相近的图片组
    best_start = 0
    min_ratio_diff = float('inf')
    
    for i in range(len(image_info) - count + 1):
        group = image_info[i:i+count]
        ratio_diff = group[-1][1] - group[0][1]  # 组内最大宽高比差异
        if ratio_diff < min_ratio_diff:
            min_ratio_diff = ratio_diff
            best_start = i
    
    # 从最佳组中选择图片
    best_group = image_info[best_start:best_start+count]
    return [path for path, _ in best_group]

def get_article_count() -> int:
    """获取文章序号"""
    count_file = 'article_count.txt'
    try:
        with open(count_file, 'r') as f:
            count = int(f.read().strip())
        return count
    except:
        return 3  # 默认从3开始

def update_article_count(count: int):
    """更新文章序号"""
    with open('article_count.txt', 'w') as f:
        f.write(str(count))

def create_article(wechat=None, image_paths=None):
    """创建文章内容"""
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
                    # 不再使用占位符URL
                    continue
            else:
                print(f'图片不存在: {img_path}')
                continue
    
    if not image_urls:
        print('没有成功上传的图片，无法创建文章')
        return None
    
    # 确保图片数量为偶数
    if len(image_urls) % 2 != 0:
        image_urls = image_urls[:-1]
    
    # 动态生成两列图片布局的HTML模板
    html_content = ''
    for i in range(0, len(image_urls), 2):
        # 最后一组图片的margin-bottom设置为15px，其他组设置为20px
        margin_bottom = '15px' if i == len(image_urls) - 2 else '20px'
        
        html_content += f'''
    <div style="display: flex; justify-content: space-between; margin-bottom: {margin_bottom};">
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; margin-right: 5px;">
            <img src="{image_urls[i]}" alt="图片{i+1}" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
        <div style="width: 95%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden;">
            <img src="{image_urls[i+1]}" alt="图片{i+2}" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
    </div>
    '''
    
    # 获取文章序号
    count = get_article_count()
    
    article_data = {
        'title': f'女朋友壁纸 | 第{count}弹来咯',
        'author': 'hao',
        'digest': f'精选女朋友壁纸第{count}期',
        'content': html_content,
        'thumb_media_id': None,
        'need_open_comment': 1,
        'only_fans_can_comment': 0
    }
    
    # 更新文章序号
    update_article_count(count + 1)
    
    return [article_data]

def main():
    # 加载配置
    config = load_config()
    
    try:
        # 获取一个未处理的目录
        selected_dir = get_unprocessed_directory(config)
        if not selected_dir:
            print('没有可处理的目录，程序退出')
            return
        
        print(f'选择处理目录: {selected_dir}')
        
        # 初始化公众号文章发布器
        wechat = WeChatArticle(config['appid'], config['appsecret'])

        # 从选定目录随机选择3张图片作为封面
        print('正在创建随机拼接封面...')
        cover_images = get_random_images(selected_dir, 3)
        if not cover_images:
            print('无法获取封面图片，程序退出')
            return
        
        merged_cover_path = 'merged_cover.jpg'
        merged_cover_path = create_merged_cover(selected_dir, merged_cover_path)
        print('封面图片已创建:')
        print(check_image(merged_cover_path))
        
        # 压缩封面图片
        print('\n正在压缩封面图片...')
        thumb_image_path = compress_image(merged_cover_path, 'thumb_merged_cover.jpg')
        print(check_image(thumb_image_path))
        
        # 上传封面图片
        print('\n正在上传封面图片...')
        result = wechat.upload_permanent_material(thumb_image_path, 'thumb')
        thumb_media_id = result['media_id']
        print(f'封面图片上传成功，media_id: {thumb_media_id}')

        # 从选定目录获取所有图片作为文章内容
        content_images = get_random_images(selected_dir)
        
        # 准备文章内容
        articles = create_article(wechat=wechat, image_paths=content_images)
        if not articles:  # 如果没有成功创建文章
            print('创建文章失败，程序退出')
            return
            
        articles[0]['thumb_media_id'] = thumb_media_id

        # 创建草稿
        print('正在创建草稿...')
        media_id = wechat.create_draft(articles)
        print(f'草稿创建成功，media_id: {media_id}')

        # 询问是否要发布文章
        publish_choice = input('是否要发布文章？(y/n): ').lower()
        if publish_choice == 'y':
            # 询问是否要群发
            mass_choice = input('是否要群发文章？(y/n): ').lower()
            if mass_choice == 'y':
                # 询问是否发送给全部用户
                is_to_all = input('是否发送给全部用户？(y/n): ').lower() == 'y'
                tag_id = None
                if not is_to_all:
                    tag_id = int(input('请输入标签ID: '))
                
                # 询问是否忽略原创校验
                ignore_reprint = input('是否忽略原创校验？(y/n): ').lower() == 'y'
                
                print('正在群发文章...')
                result = wechat.send_mass_message(
                    media_id,
                    send_ignore_reprint=1 if ignore_reprint else 0,
                    is_to_all=is_to_all,
                    tag_id=tag_id
                )
                print(f'群发任务创建成功，msg_id: {result["msg_id"]}')
                
                # 等待一段时间后查询群发状态
                print('等待30秒后查询群发状态...')
                time.sleep(30)
                status = wechat.get_mass_status(result['msg_id'])
                print(f'群发状态: {status}')
            else:
                # 普通发布
                print('正在发布文章...')
                publish_id = wechat.publish_draft(media_id)
                print(f'发布任务创建成功，publish_id: {publish_id}')
                status = wechat.wait_for_publish(publish_id)
                if status['publish_status'] == 0:
                    print('文章发布成功！')
                    if 'article_detail' in status:
                        for item in status['article_detail']['item']:
                            print(f'文章链接: {item["article_url"]}')
                else:
                    print(f'发布失败: {status["status_desc"]}')

    except Exception as e:
        print(f'发生错误: {str(e)}')

if __name__ == '__main__':
    main()