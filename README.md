# 微信公众号自动发布系统

这是一个用于自动处理图片并发布到微信公众号的工具集。

## 功能特点

- 自动处理和压缩图片，确保符合微信公众号要求
- 创建合并封面图片
- 自动发布文章到微信公众号
- 支持批量处理图片目录

## 目录结构

```
/
├── config/                  # 配置文件目录
│   └── config.json          # 主配置文件
├── core/                    # 核心功能模块
│   ├── wechat_article.py    # 微信公众号文章发布核心类
│   ├── create_cover.py      # 封面图片创建功能
│   ├── check_image.py       # 图片检查功能
│   └── compress_image.py    # 图片压缩功能
├── utils/                   # 工具函数
│   ├── convert_jpeg.py      # 图片格式转换工具
│   └── extract_images.py    # 图片提取工具
├── scripts/                 # 脚本目录
│   ├── publish_auto.py      # 自动发布脚本
│   ├── publish_demo.py      # 示例发布脚本
│   └── publish_with_merged_cover.py  # 使用合并封面发布脚本
├── data/                    # 数据目录
│   └── processed_dirs.json  # 已处理目录记录
|   └── articl_count.txt  # 已处理目录记录
├── templates/               # 模板目录
│   └── temple.html          # HTML模板
├── img/                     # 处理后的图片目录
├── imgs/                    # 原始图片目录
└── fengmian/                # 封面图片目录
```

## 使用方法

1. 在`config/config.json`中配置微信公众号的appid和appsecret
2. 将需要处理的图片放入`imgs`目录
3. 运行相应的发布脚本：
   - `python scripts/publish_auto.py` - 自动选择未处理的目录并发布
   - `python scripts/publish_demo.py` - 发布示例文章
   - `python scripts/publish_with_merged_cover.py` - 使用合并封面发布文章

## 文件说明

- **wechat_article.py**: 微信公众号文章发布的核心类，处理认证、图片上传和文章发布
- **create_cover.py**: 创建合并封面图片的功能
- **check_image.py**: 检查图片是否符合微信公众号要求
- **compress_image.py**: 压缩图片以符合大小限制
- **convert_jpeg.py**: 转换图片格式
- **extract_images.py**: 从源目录提取图片到目标目录
- **publish_auto.py**: 自动选择未处理的目录并发布文章
- **publish_demo.py**: 发布示例文章的脚本
- **publish_with_merged_cover.py**: 使用合并封面发布文章的脚本