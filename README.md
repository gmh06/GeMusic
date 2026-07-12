# GeMusic

**葛沐昊 2025010563**

---

基于 Playwright 爬虫 + Django 的音乐数据展示网站 + 数据分析，爬取 QQ 音乐相关信息。

## 项目结构

```
music_web/
├── crawler/ # 爬虫模块
│   ├── main.py # 主程序入口
│   ├── robot.py
│   ├── get_singers.py
│   ├── get_songs.py
│   ├── config.json # 登录配置不提交到 Git
│   ├── UA_list.json
│   └── data/ # 爬虫原始数据不提交到 Git
├── GeMusic_site/ # 网站模块
│   ├── manage.py
│   ├── db.sqlite3 # 数据库文件不提交到 Git
│   ├── GeMusic/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── migrations/
│   │   ├── static/ # 静态资源图片不提交到 Git
│   │   └── templates/
│   └── GeMusic_site/
│       ├── settings.py
│       ├── secret_key.txt # SECRET_KEY 不提交到 Git
│       └── urls.py
├── report/ # 报告模块
│   ├── analyze_report/ # 数据分析报告
│   └── project_report/ # 项目报告
├── import_data.py # 数据迁移脚本
├── analyze.ipynb # 数据分析
├── .gitignore
└── README.md
```

## 相关技术

| 技术 | 用途 |
|------|------|
| Python | 编程语言 |
| Playwright (async) | 异步浏览器自动化爬虫 |
| Django | Web 框架 |
| SQLite | 数据库 |
| Jupyter Notebook | 数据分析 |

## 快速开始

### 1. 依赖

```bash
pip install django playwright tqdm
playwright install chromium

# 数据分析
pip install numpy matplotlib seaborn pandas jupyter
```

### 2. 创建 SECRET_KEY

在 `GeMusic_site/` 目录下创建 `secret_key.txt`，内容为任意长字符串（一行即可）：

```
your-secret-key-here-make-it-long-and-random
```

### 3. 获取爬虫登录凭证

```bash
cd crawler
python main.py --login
```

此命令会打开浏览器，手动在浏览器中登录 QQ 音乐后，回到命令行按回车，cookie 会保存到 `config.json`。

### 4. 运行爬虫

```bash
python main.py
```

爬虫会依次爬取歌手和歌曲信息，数据保存在 `crawler/data/`。

### 5. 数据迁移到 Django

```bash
# 回到项目根目录
cd ..

# 创建数据库迁移（首次运行）
cd GeMusic_site
python manage.py makemigrations
python manage.py migrate
cd ..

# 导入爬虫数据 + 复制图片到 static/
python import_data.py
```

### 6. 启动服务器

```bash
cd GeMusic_site
python manage.py runserver
```

访问：http://localhost:8000

## 数据迁移说明

本项目采用**代码与数据分离**的设计：

- `crawler/data/`、`GeMusic_site/db.sqlite3`、`GeMusic_site/GeMusic/static/` 均不包含在 Git 中
- 运行 `import_data.py` 可将爬虫数据导入 Django 数据库，并复制图片到 static 目录
- 任何时候都可以通过重新爬取 + 迁移来重建数据