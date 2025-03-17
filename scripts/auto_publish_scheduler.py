import os
import sys
import time
import json
import random
import logging
from datetime import datetime
from functools import wraps

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

# 导入核心模块
from core.wechat_article import WeChatArticle
from core.create_cover import create_merged_cover
from core.check_image import check_image
from core.compress_image import compress_image

# 配置日志
# 确保日志目录存在
os.makedirs(os.path.join(root_dir, 'logs'), exist_ok=True)
os.makedirs(os.path.join(root_dir, 'data'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_dir, 'logs', 'auto_publish.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def retry_on_error(max_retries=3, delay=5):
    """错误重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f'{func.__name__} 最终失败: {str(e)}')
                        raise
                    logger.warning(f'{func.__name__} 失败，正在重试 ({retries}/{max_retries}): {str(e)}')
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_error(max_retries=3)
def load_config(config_path: str = os.path.join(root_dir, 'config', 'config.json')) -> dict:
    """加载配置文件"""
    if not os.path.exists(config_path):
        config = {
            'appid': 'wx068a368be317edd0',
            'appsecret': '5a2d58d2f0c47c44c5d5fed196f7b96d'
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logger.error(f'请先在{config_path}中配置公众号的appid和appsecret')
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@retry_on_error(max_retries=3)
def get_unprocessed_directory(config: dict) -> str:
    """获取未处理的目录"""
    base_dir = config.get('image_base_dir', os.path.join(root_dir, 'imgs'))
    processed_dirs_file = os.path.join(root_dir, 'data', 'processed_dirs.json')
    
    try:
        with open(processed_dirs_file, 'r', encoding='utf-8') as f:
            processed_dirs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        processed_dirs = []
    
    all_dirs = []
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            dir_path = os.path.join(root, d)
            all_dirs.append(dir_path)
    
    unprocessed_dirs = [d for d in all_dirs if d not in processed_dirs]
    
    if not unprocessed_dirs:
        logger.info('所有目录都已处理完毕')
        return None
    
    selected_dir = random.choice(unprocessed_dirs)
    processed_dirs.append(selected_dir)
    
    os.makedirs(os.path.dirname(processed_dirs_file), exist_ok=True)
    with open(processed_dirs_file, 'w', encoding='utf-8') as f:
        json.dump(processed_dirs, f, indent=4, ensure_ascii=False)
    
    return selected_dir

@retry_on_error(max_retries=3)
def get_article_count() -> int:
    """获取文章序号"""
    count_file = os.path.join(root_dir, 'data', 'article_count.txt')
    try:
        with open(count_file, 'r') as f:
            count = int(f.read().strip())
        return count
    except:
        return 3

@retry_on_error(max_retries=3)
def update_article_count(count: int):
    """更新文章序号"""
    count_file = os.path.join(root_dir, 'data', 'article_count.txt')
    os.makedirs(os.path.dirname(count_file), exist_ok=True)
    with open(count_file, 'w') as f:
        f.write(str(count))

@retry_on_error(max_retries=3)
def create_article(wechat, image_paths):
    """创建文章内容"""
    image_urls = []
    for img_path in image_paths:
        if os.path.exists(img_path):
            try:
                url = wechat.upload_article_image(img_path)
                image_urls.append(url)
                logger.info(f'图片上传成功: {url}')
            except Exception as e:
                logger.error(f'图片上传失败: {str(e)}')
                continue
        else:
            logger.error(f'图片不存在: {img_path}')
            continue
    
    if not image_urls:
        logger.error('没有成功上传的图片，无法创建文章')
        return None
    
    if len(image_urls) % 2 != 0:
        image_urls = image_urls[:-1]
    
    html_content = ''
    for i in range(len(image_urls)):
        margin_bottom = '5px' if i == len(image_urls) - 1 else '8px'
        html_content += f'''
    <div style="margin-bottom: {margin_bottom};">
        <div style="width: 100%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden;">
            <img src="{image_urls[i]}" alt="图片{i+1}" style="width: 100%; height: auto; object-fit: cover; display: block;"/>
        </div>
    </div>
    '''
    
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
    
    update_article_count(count + 1)
    return [article_data]

@retry_on_error(max_retries=3)
def get_random_images(folder: str, count: int = None) -> list:
    """从指定文件夹及其子目录随机选择图片，确保选择的图片具有相似的宽高比
    
    Args:
        folder: 根目录路径
        count: 需要的图片数量，如果为None则返回所有图片
        
    Returns:
        list: 图片路径列表
    """
    if not os.path.exists(folder):
        logger.error(f'文件夹不存在: {folder}')
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
                    logger.error(f'读取图片失败: {f}, 错误: {str(e)}')
    
    if not image_info:
        logger.error(f'目录中没有有效图片: {folder}')
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

@retry_on_error(max_retries=3)
def auto_publish():
    """自动发布文章"""
    logger.info('开始自动发布流程')
    config = load_config()
    
    try:
        selected_dir = get_unprocessed_directory(config)
        if not selected_dir:
            logger.info('没有可处理的目录，程序退出')
            return
        
        logger.info(f'选择处理目录: {selected_dir}')
        wechat = WeChatArticle(config['appid'], config['appsecret'])

        # 创建和上传封面
        logger.info('正在创建随机拼接封面...')
        cover_images = get_random_images(selected_dir, 3)
        if not cover_images:
            logger.error('无法获取封面图片，程序退出')
            return
        
        merged_cover_path = os.path.join(root_dir, 'merged_cover.jpg')
        merged_cover_path = create_merged_cover(selected_dir, merged_cover_path)
        logger.info('封面图片已创建')
        logger.info(check_image(merged_cover_path))
        
        thumb_image_path = os.path.join(root_dir, 'thumb_merged_cover.jpg')
        thumb_image_path = compress_image(merged_cover_path, thumb_image_path)
        logger.info('封面图片已压缩')
        logger.info(check_image(thumb_image_path))
        
        result = wechat.upload_permanent_material(thumb_image_path, 'thumb')
        thumb_media_id = result['media_id']
        logger.info(f'封面图片上传成功，media_id: {thumb_media_id}')

        # 准备文章内容
        content_images = get_random_images(selected_dir)
        articles = create_article(wechat=wechat, image_paths=content_images)
        if not articles:
            logger.error('创建文章失败，程序退出')
            return
        
        articles[0]['thumb_media_id'] = thumb_media_id

        # 创建草稿
        logger.info('正在创建草稿...')
        media_id = wechat.create_draft(articles)
        logger.info(f'草稿创建成功，media_id: {media_id}')

        # 群发文章
        logger.info('正在群发文章...')
        result = wechat.send_mass_message(
            media_id,
            send_ignore_reprint=1,  # 忽略原创校验
            is_to_all=True,  # 发送给所有用户
            tag_id=None
        )
        logger.info(f'群发任务创建成功，msg_id: {result["msg_id"]}')
        
        # 等待并检查群发状态
        logger.info('等待30秒后查询群发状态...')
        time.sleep(30)
        status = wechat.get_mass_status(result['msg_id'])
        logger.info(f'群发状态: {status}')

    except Exception as e:
        logger.error(f'发布过程出错: {str(e)}')
        raise

def wait_until_8am():
    """等待到早上8点"""
    now = datetime.now()
    target = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if now >= target:
        target = target.replace(day=target.day + 1)
    wait_seconds = (target - now).total_seconds()
    logger.info(f'等待{wait_seconds}秒后开始发布...')
    time.sleep(wait_seconds)

def main():
    """主函数"""
    # 创建必要的目录
    logs_dir = os.path.join(root_dir, 'logs')
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    
    # 重新配置日志，确保日志目录存在后再配置
    log_file = os.path.join(logs_dir, 'auto_publish.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    while True:
        try:

            wait_until_8am()
            auto_publish()

        except Exception as e:
            logger.error(f'运行出错: {str(e)}')
        # 无论成功失败，都等待到下一个8点

if __name__ == '__main__':
    main()