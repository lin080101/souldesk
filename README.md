# souldesk
SoulDesk 是一个基于云服务器的跨平台远程控制系统，允许用户通过手机网页（或打包成APP）实时监控和控制电脑状态。

注意：作者目前已在安卓端和Windows端完成实测，其他平台暂未提供完整测试数据

## ✨ 核心功能

### 🖥️ 状态监控

实时获取电脑锁屏状态

实时监控系统音量状态

电脑在线状态实时检测

### 📱 远程控制

远程锁屏/解锁操作

系统关机远程执行

跨平台音量控制

一键静音/取消静音

### 🔁 双向通信
通过云端服务器实现数据同步

状态变化实时推送

响应式手机控制界面

## 🚀 部署方法

一、云服务器部署 (Python 3.7+)

bash
# 安装依赖
pip3 install websockets

# 启动服务器
python3 server.py
监听端口：

8822 (TCP/PC客户端)

8823 (WebSocket/手机端)

无云服务器解决方案：
使用内网穿透服务：

飞鸽内网穿透教程

星空内网穿透教程

二、PC客户端部署
Windows 依赖安装：

bash
pip3 install pycaw pywin32
macOS/Linux 依赖安装：

bash
# macOS
brew install osascript

# Linux (Debian/Ubuntu)
sudo apt-get install xflock4 gnome-screensaver
配置修改 (main.py):

python
# 修改为你的服务器公网IP
server_ip = 'your.server.ip'
运行客户端：

bash
python3 main.py
三、手机控制端部署
将 index.html 部署到云服务器（端口：8821）

修改服务器地址（HTML 第537行）：

javascript
// 修改为你的服务器IP
ws = new WebSocket('ws://your.server.ip:8823');
📲 使用流程
启动云服务器

在目标电脑运行PC客户端

手机访问部署好的 index.html

点击"连接服务器"按钮

控制面板功能：

🖥️ 电脑控制：锁屏/关机

🔊 音量控制：静音/取消/滑块调节

⚠️ 注意事项
防火墙配置
确保开放以下端口：

8821 (HTTP/HTTPS)

8822 (TCP)

8823 (WebSocket)

平台支持差异
功能	Windows	macOS	Linux
锁屏检测	✅	⚠️ 部分支持	⚠️ 需要额外配置
音量控制	✅	✅	⚠️ 需要PulseAudio
远程关机	✅	✅	✅
状态实时推送	✅	✅	✅
Linux 特殊配置：

bash
# Debian/Ubuntu
sudo apt-get install xflock4 gnome-screensaver pulseaudio

# Arch Linux
sudo pacman -S xss-lock gnome-screensaver pulseaudio
