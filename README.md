
# Video-Downloader-Software

This is a video downloading tool based on yt-dlp. It supports downloading YouTube and Bilibili videos using personal account cookies, which enables the download of members-only videos.

这是一个基于 yt-dlp 的视频下载工具，支持使用个人账号 cookies 的 YouTube 和 Bilibili 视频下载，可以实现会员限定视频下载。



## 🚀 Features

**中文**
* 基于 `yt-dlp` 构建，支持高速提取和解析 YouTube 和 Bilibili 视频链接。
* **全格式展示**：一键获取视频的所有可用格式，以直观的表格呈现（包含格式 ID、扩展名、分辨率、帧率、文件大小及音视频编码）。
* **自由组合下载**：支持表格多选（Multi-Selection），允许用户自由组合下载指定的视频轨与音频轨。
* **Cookie 导入**：原生支持选择本地 `cookies.txt` 文件，轻松下载需要登录的视频（如会员专属视频）。


## 📖 使用方法 (Usage)

只需简单的几个步骤，即可开始下载你喜欢的视频：

### 1. 准备环境
首先，确保你的电脑已安装 Python (建议 3.10 或以上版本)。在项目根目录打开终端，运行以下命令来安装所需依赖：
```bash
pip install -r requirements.txt
```

### 2. 运行程序
在终端中执行以下命令启动图形界面：
```bash
python yt_down_ui.py
```

### 3. 操作指南
* **输入链接**：在 `输入视频路径` 处粘贴需要下载的视频 URL。
* **配置 Cookie**：在 `选择 Cookie` 处导入你的本地 cookies 文件。
  > 💡 **提示**：如果你不知道如何提取账号 Cookie，请参考这篇 [Cookie 获取教程](https://www.bilibili.com/opus/976869609795747864)。
* **选择路径**：设定视频下载后的保存文件夹。
* **解析与选择**：
  * 点击 `获取解析格式`，等待表格刷新出所有可下载的格式。
  * 鼠标点击选中你想要下载的格式。
  * ⚠️ **音视频合并需知**：如果你想下载分离的高清视频和高质量音频并让它们自动合并，请**同时选中**一个视频轨和一个音频轨。注意：此合并功能要求你的系统已正确安装并配置好 `ffmpeg`。如果未安装，建议仅单选一个自带声音的视频格式。
* **开始下载**：点击 `开始下载所选内容`，即可在下方的运行日志中查看实时进度！


## Related

感谢以下项目的支持：

[yt-dlp](https://github.com/yt-dlp/yt-dlp)

