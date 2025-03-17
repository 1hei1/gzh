import json
import time
import os
import requests
from typing import List, Dict, Union, Optional

class WeChatArticle:
    def __init__(self, appid: str, appsecret: str):
        """初始化微信公众号文章发布器

        Args:
            appid: 微信公众号的AppID
            appsecret: 微信公众号的AppSecret
        """
        self.appid = appid
        self.appsecret = appsecret
        self.access_token = None
        self.token_expires = 0

    def _get_access_token(self) -> str:
        """获取或刷新access_token

        Returns:
            str: 有效的access_token
        """
        if self.access_token and time.time() < self.token_expires - 300:  # 提前5分钟刷新
            return self.access_token

        url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}'
        response = requests.get(url)
        result = response.json()

        if 'access_token' in result:
            self.access_token = result['access_token']
            self.token_expires = time.time() + result['expires_in']
            return self.access_token
        else:
            raise Exception(f'获取access_token失败: {result}')

    def upload_image(self, image_path: str, type: str = 'image') -> str:
        """上传图片素材

        Args:
            image_path: 图片文件路径
            type: 素材类型，可选值：image（临时）或thumb（永久缩略图）

        Returns:
            str: 媒体文件ID（media_id）
        """
        # 检查文件大小限制
        file_size = os.path.getsize(image_path) / (1024 * 1024)  # 转换为MB
        if type == 'thumb' and file_size > 0.064:  # 缩略图限制64KB
            raise Exception(f'缩略图大小（{file_size:.2f}MB）超过64KB限制')
        elif type == 'image' and file_size > 10:  # 普通图片限制10MB
            raise Exception(f'图片大小（{file_size:.2f}MB）超过10MB限制')

        url = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={self._get_access_token()}&type={type}'
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
            result = response.json()
            print(result)

            if 'media_id' in result:
                return result['media_id']
            elif 'thumb_media_id' in result:  # 处理缩略图上传的特殊返回格式
                return result['thumb_media_id']
            else:
                raise Exception(f'上传图片失败: {result}')

    def upload_article_image(self, image_path: str) -> str:
        """上传图文消息内的图片获取URL

        Args:
            image_path: 图片文件路径

        Returns:
            str: 图片URL
        """
        # 压缩图片
        from PIL import Image
        import io

        # 读取原始图片
        with Image.open(image_path) as img:
            # 计算新的分辨率（保持宽高比，最大宽度为1920像素）
            max_width = 1920
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 将图片转换为JPEG格式并压缩
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            # 上传压缩后的图片
            url = f'https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={self._get_access_token()}'
            files = {'media': ('image.jpg', output, 'image/jpeg')}
            response = requests.post(url, files=files)
            result = response.json()

            if 'url' in result:
                return result['url']
            else:
                raise Exception(f'上传文章图片失败: {result}')

    def create_draft(self, articles: List[Dict]) -> str:
        """创建草稿

        Args:
            articles: 图文消息列表，每个图文消息是一个字典，包含必要的字段

        Returns:
            str: 草稿的media_id
        """
        url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self._get_access_token()}'
        data = {
            'articles': articles
        }
        # 使用ensure_ascii=False确保中文字符不会被转义为Unicode编码
        json_data = json.dumps(data, ensure_ascii=False)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.post(url, data=json_data.encode('utf-8'), headers=headers)
        result = response.json()

        if 'media_id' in result:
            return result['media_id']
        else:
            raise Exception(f'创建草稿失败: {result}')

    def publish_draft(self, media_id: str) -> str:
        """发布草稿

        Args:
            media_id: 要发布的草稿的media_id

        Returns:
            str: 发布任务的ID（publish_id）
        """
        url = f'https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={self._get_access_token()}'
        data = {
            'media_id': media_id
        }
        response = requests.post(url, json=data)
        result = response.json()

        if result.get('errcode') == 0:
            return result['publish_id']
        else:
            raise Exception(f'发布草稿失败: {result}')

    def get_publish_status(self, publish_id: str) -> Dict:
        """获取发布状态

        Args:
            publish_id: 发布任务的ID

        Returns:
            Dict: 发布状态信息
        """
        url = f'https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={self._get_access_token()}'
        data = {
            'publish_id': publish_id
        }
        response = requests.post(url, json=data)
        result = response.json()

        status_map = {
            0: '发布成功',
            1: '发布中',
            2: '原创失败',
            3: '常规失败',
            4: '平台审核不通过',
            5: '成功后用户删除所有文章',
            6: '成功后系统封禁所有文章'
        }

        if 'publish_status' in result:
            result['status_desc'] = status_map.get(result['publish_status'], '未知状态')
            return result
        else:
            raise Exception(f'获取发布状态失败: {result}')

    def wait_for_publish(self, publish_id: str, timeout: int = 300, interval: int = 5) -> Dict:
        """等待发布完成

        Args:
            publish_id: 发布任务的ID
            timeout: 超时时间（秒）
            interval: 轮询间隔（秒）

        Returns:
            Dict: 最终的发布状态信息
        """
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise Exception('发布等待超时')

            status = self.get_publish_status(publish_id)
            if status['publish_status'] != 1:  # 不是发布中状态
                return status

            time.sleep(interval)

    def upload_permanent_material(self, file_path: str, type: str = 'image') -> Dict:
        """上传永久素材

        Args:
            file_path: 文件路径
            type: 素材类型，可选值：image（图片）、voice（语音）、video（视频）、thumb（缩略图）

        Returns:
            Dict: 包含上传结果的字典，永久图片素材会返回url
        """
        # 检查文件大小和格式限制
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        if type == 'thumb' and file_size > 2:  # 缩略图限制2mb
            raise Exception(f'缩略图大小（{file_size:.2f}MB）超过64KB限制')
        elif type == 'image' and file_size > 10:  # 图片限制10MB
            raise Exception(f'图片大小（{file_size:.2f}MB）超过10MB限制')
        elif type == 'voice' and file_size > 2:  # 语音限制2MB
            raise Exception(f'语音大小（{file_size:.2f}MB）超过2MB限制')
        elif type == 'video' and file_size > 10:  # 视频限制10MB
            raise Exception(f'视频大小（{file_size:.2f}MB）超过10MB限制')

        url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self._get_access_token()}&type={type}'
        with open(file_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
            result = response.json()

            if 'media_id' in result:
                return result
            else:
                raise Exception(f'上传永久素材失败: {result}')

    def send_mass_message(self, media_id: str, send_ignore_reprint: int = 0, is_to_all: bool = True, tag_id: Optional[int] = None) -> Dict:
        """群发图文消息

        Args:
            media_id: 图文消息的media_id
            send_ignore_reprint: 图文消息被判定为转载时，是否继续群发。0为停止群发，1为继续群发
            is_to_all: 是否发送给全部用户
            tag_id: 群发到的标签的tag_id，is_to_all为False时必填

        Returns:
            Dict: 群发结果
        """
        if not is_to_all and tag_id is None:
            raise Exception('发送给指定标签时必须提供tag_id')

        url = f'https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={self._get_access_token()}'
        data = {
            'filter': {
                'is_to_all': is_to_all,
                'tag_id': tag_id if not is_to_all else 0
            },
            'mpnews': {
                'media_id': media_id
            },
            'msgtype': 'mpnews',
            'send_ignore_reprint': send_ignore_reprint
        }
        response = requests.post(url, json=data)
        result = response.json()

        if result.get('errcode') == 0:
            return result
        else:
            raise Exception(f'群发消息失败: {result}')

    def get_mass_status(self, msg_id: str) -> Dict:
        """查询群发消息发送状态

        Args:
            msg_id: 群发消息的msg_id

        Returns:
            Dict: 群发状态信息
        """
        url = f'https://api.weixin.qq.com/cgi-bin/message/mass/get?access_token={self._get_access_token()}'
        data = {
            'msg_id': msg_id
        }
        response = requests.post(url, json=data)
        result = response.json()

        if result.get('msg_status') == 'SEND_SUCCESS':
            return result
        else:
            raise Exception(f'查询群发状态失败: {result}')

    def delete_mass_message(self, msg_id: str, article_idx: Optional[int] = None) -> Dict:
        """删除群发消息

        Args:
            msg_id: 群发消息的msg_id
            article_idx: 要删除的文章在图文消息中的位置，第一篇为1，不填或为0会删除全部文章

        Returns:
            Dict: 删除结果
        """
        url = f'https://api.weixin.qq.com/cgi-bin/message/mass/delete?access_token={self._get_access_token()}'
        data = {
            'msg_id': msg_id,
            'article_idx': article_idx if article_idx else 0
        }
        response = requests.post(url, json=data)
        result = response.json()

        if result.get('errcode') == 0:
            return result
        else:
            raise Exception(f'删除群发消息失败: {result}')