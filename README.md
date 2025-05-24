# Google Maps Scraper / Google Maps 抓取器

[English](#english) | [中文](#中文)

---

## English

A powerful scraper for Google Maps reviews and place information. This tool extracts comprehensive data including reviews, place metadata, ratings, contact information, and geographical coordinates from Google Maps Points of Interest (POI).

### ✨ Features

- **Place Information Extraction**: Name, category, address, phone number, website, Plus Code, coordinates
- **Review Scraping**: Extract user reviews with ratings, dates, and user information  
- **Flexible Sorting**: Sort reviews by relevance, date, or rating
- **Geographic Data**: Automatic extraction of latitude and longitude coordinates
- **Multiple Output Formats**: CSV output with comprehensive data fields
- **Debug Mode**: Visual browser interface for debugging
- **Robust Error Handling**: Handles various page structures and missing data

### 🛠 Installation

#### Prerequisites
- Python >= 3.9
- Chrome browser installed

#### Setup Steps

1. **Install Python Dependencies**
   ```bash
   # Using conda (recommended)
   conda create --name scraping python=3.9
   conda activate scraping
   pip install -r requirements.txt
   
   # Or using pip directly
   pip install -r requirements.txt
   ```

2. **Chrome Driver Setup**
   - The scraper automatically downloads and manages ChromeDriver using `webdriver-manager`
   - No manual ChromeDriver installation required!

### 📖 Usage

#### Basic Usage

```bash
python scraper.py --i input/urls.txt --o output.csv --N 50
```

#### Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--i` | Input file with Google Maps URLs | `urls.txt` | `input/test_urls.txt` |
| `--o` | Output CSV filename | `output.csv` | `my_data.csv` |
| `--N` | Number of reviews to scrape | `100` | `50` |
| `--sort_by` | Review sorting method | `newest` | `most_relevant`, `newest`, `highest_rating`, `lowest_rating` |
| `--debug` | Enable visual browser mode | `False` | `--debug` |

#### Examples

```bash
# Scrape 100 newest reviews
python scraper.py --i urls.txt --o reviews.csv --N 100

# Scrape 50 highest-rated reviews with debug mode
python scraper.py --i urls.txt --o top_reviews.csv --N 50 --sort_by highest_rating --debug

# Quick test with debug mode
python scraper.py --i input/test_urls.txt --o test.csv --N 10 --debug
```

### 📊 Output Data Fields

The scraper extracts the following information:

#### Place Information
- `place_name`: Name of the establishment
- `overall_rating`: Average rating (1-5 stars)
- `n_reviews`: Total number of reviews
- `n_photos`: Number of photos
- `category`: Business category (e.g., "Restaurant", "Hotel")
- `description`: Place description
- `address`: Full address
- `website`: Official website
- `phone_number`: Contact phone number
- `plus_code`: Google Plus Code
- `opening_hours`: Operating hours
- `lat`: Latitude coordinate
- `long`: Longitude coordinate

#### Review Information
- `id_review`: Unique review identifier
- `caption`: Review text content
- `relative_date`: When the review was posted
- `retrieval_date`: When the data was scraped
- `rating`: Review rating (1-5 stars)
- `username`: Reviewer's name
- `n_review_user`: Number of reviews by this user
- `url_user`: Link to reviewer's profile

### 🔗 URL Format

To get the correct Google Maps URL:

1. Go to Google Maps and search for a place
2. Click on the place to open its details
3. Click on the reviews section
4. Copy the URL from your browser

Example URL format:
```
https://www.google.com/maps?cid=1234567890123456789&hl=en
```

### 🐛 Debugging

If you encounter issues:

1. **Enable Debug Mode**: Add `--debug` flag to see the browser in action
2. **Check URLs**: Ensure URLs are in the correct format (see example above)
3. **Reduce Sample Size**: Start with `--N 5` for testing
4. **Check Logs**: Review `gm-scraper.log` for detailed error information

### 📝 Recent Updates

- ✅ **Fixed Place Information Extraction**: Updated CSS selectors for Google Maps' new page structure
- ✅ **Enhanced Coordinate Detection**: Automatic extraction from JavaScript data
- ✅ **Improved Field Recognition**: Better detection of Plus Codes, addresses, and contact info
- ✅ **Robust Error Handling**: Graceful handling of missing data and page variations
- ✅ **Multiple Fallback Methods**: Multiple strategies for data extraction

---

## 中文

一个强大的Google Maps评论和地点信息抓取工具。该工具可以从Google Maps兴趣点(POI)中提取包括评论、地点元数据、评分、联系信息和地理坐标在内的综合数据。

### ✨ 功能特点

- **地点信息提取**: 名称、类别、地址、电话、网站、Plus Code、坐标
- **评论抓取**: 提取用户评论及评分、日期和用户信息
- **灵活排序**: 按相关性、日期或评分排序评论
- **地理数据**: 自动提取经纬度坐标
- **多种输出格式**: 包含全面数据字段的CSV输出
- **调试模式**: 可视化浏览器界面用于调试
- **强大的错误处理**: 处理各种页面结构和缺失数据

### 🛠 安装步骤

#### 前置要求
- Python >= 3.9
- 已安装Chrome浏览器

#### 安装步骤

1. **安装Python依赖**
   ```bash
   # 使用conda（推荐）
   conda create --name scraping python=3.9
   conda activate scraping
   pip install -r requirements.txt
   
   # 或直接使用pip
   pip install -r requirements.txt
   ```

2. **Chrome驱动设置**
   - 抓取器使用`webdriver-manager`自动下载和管理ChromeDriver
   - 无需手动安装ChromeDriver！

### 📖 使用方法

#### 基本用法

```bash
python scraper.py --i input/urls.txt --o output.csv --N 50
```

#### 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--i` | 包含Google Maps URL的输入文件 | `urls.txt` | `input/test_urls.txt` |
| `--o` | 输出CSV文件名 | `output.csv` | `my_data.csv` |
| `--N` | 要抓取的评论数量 | `100` | `50` |
| `--sort_by` | 评论排序方式 | `newest` | `most_relevant`, `newest`, `highest_rating`, `lowest_rating` |
| `--debug` | 启用可视化浏览器模式 | `False` | `--debug` |

#### 使用示例

```bash
# 抓取100条最新评论
python scraper.py --i urls.txt --o reviews.csv --N 100

# 抓取50条最高评分的评论，启用调试模式
python scraper.py --i urls.txt --o top_reviews.csv --N 50 --sort_by highest_rating --debug

# 使用调试模式进行快速测试
python scraper.py --i input/test_urls.txt --o test.csv --N 10 --debug
```

### 📊 输出数据字段

抓取器提取以下信息：

#### 地点信息
- `place_name`: 场所名称
- `overall_rating`: 平均评分（1-5星）
- `n_reviews`: 评论总数
- `n_photos`: 照片数量
- `category`: 业务类别（如"餐厅"、"酒店"）
- `description`: 地点描述
- `address`: 完整地址
- `website`: 官方网站
- `phone_number`: 联系电话
- `plus_code`: Google Plus Code
- `opening_hours`: 营业时间
- `lat`: 纬度坐标
- `long`: 经度坐标

#### 评论信息
- `id_review`: 唯一评论标识符
- `caption`: 评论文本内容
- `relative_date`: 评论发布时间
- `retrieval_date`: 数据抓取时间
- `rating`: 评论评分（1-5星）
- `username`: 评论者姓名
- `n_review_user`: 该用户的评论数量
- `url_user`: 评论者档案链接

### 🔗 URL格式

获取正确的Google Maps URL：

1. 前往Google Maps并搜索地点
2. 点击地点打开其详细信息
3. 点击评论部分
4. 从浏览器复制URL

URL格式示例：
```
https://www.google.com/maps?cid=1234567890123456789&hl=en
```

### 🐛 故障排除

如果遇到问题：

1. **启用调试模式**: 添加`--debug`标志查看浏览器操作
2. **检查URL**: 确保URL格式正确（参见上面的示例）
3. **减少样本大小**: 从`--N 5`开始测试
4. **查看日志**: 查看`gm-scraper.log`获取详细错误信息

### 📝 最近更新

- ✅ **修复地点信息提取**: 更新CSS选择器以适配Google Maps新页面结构
- ✅ **增强坐标检测**: 从JavaScript数据自动提取坐标
- ✅ **改进字段识别**: 更好地识别Plus Code、地址和联系信息
- ✅ **强大的错误处理**: 优雅处理缺失数据和页面变化
- ✅ **多种备用方法**: 多种数据提取策略

### 📄 许可证

本项目使用MIT许可证 - 详见[LICENSE](LICENSE)文件。

### 🤝 贡献

欢迎提交问题报告和功能请求！如需贡献代码，请先开启问题讨论您的想法。

### ⚠️ 免责声明

此工具仅供教育和研究目的。使用时请遵守Google Maps的服务条款和robots.txt规定。对于任何因使用此工具而产生的问题，开发者概不负责。
