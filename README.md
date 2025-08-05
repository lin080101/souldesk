<p align="center">
  <a href="http://ff.soul6.cn/souldesk/" target="_blank">
    <img
      width="200"
      src="http://ff.soul6.cn/souldesk/logo.png"
    />
  </a>
</p>

<h1 align="center">
  SoulDesk
</h1>
<p align="center">
  基于云服务器的跨平台远程控制系统，允许用户通过手机网页（或打包成APP）或者电脑网页（或打包成EXE）实时监控和控制电脑状态
</p>

> [!CAUTION]
> 注意：SoulDesk 作者目前已在安卓端和Windows端完成实测，其他平台暂无测试数据

SoulDesk 的由来仅仅是作者偶然的一个 idea，然后花了两天时间爆肝出来的，已经燃尽了，部分功能还有待改进和开发

SoulDesk存在的已知问题：针对检测电脑是否锁屏方面，作者实测下来有点不准，只能用歪门邪道的办法了，嘻嘻~

> 在此欢迎各位有实力的大佬，一起进行研究和开发，谢谢啦！

## 预览

快速体验(只做体验，没有实际功能)：[http://ff.soul6.cn/souldesk/](http://ff.soul6.cn/souldesk/)
<p align="center">
  <a href="http://ff.soul6.cn/souldesk/" target="_blank">
    <img
      width="200"
      src="http://ff.soul6.cn/souldesk/phone.png"
    />
  </a>
</p>

<p align="center">
  <a href="http://ff.soul6.cn/souldesk/" target="_blank">
    <img
      width="200"
      src="http://ff.soul6.cn/souldesk/pc.png"
    />
  </a>
</p>

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

### 一、云服务器部署 (Python 3.7+)

#### 安装依赖
```
pip3 install websockets
```

#### 启动服务器
```
python3 server.py
```
监听端口：8822 (TCP/PC客户端) 和 8823 (WebSocket/手机端)

### 无云服务器解决方案：

>那这里有人就会问作者了，没有云服务器咋办，当然是直接内网穿透啦！！！下面作者推荐两个平台，亲身使用过，感觉还不错
  <a href="https://blog.csdn.net/lin080101/article/details/129907651?spm=1001.2014.3001.5502" target="_blank">
    <p>飞鸽内网穿透</p>
  </a>
  <a href="https://blog.csdn.net/lin080101/article/details/135980626?spm=1001.2014.3001.5502" target="_blank">
    <p>星空内网穿透</p>
  </a>

### 二、PC客户端部署

#### Windows 依赖安装：

```
pip3 install pycaw pywin32
```

#### macOS依赖安装：

```
brew install osascript
```

#### Linux 依赖安装：

```
sudo apt-get install xflock4 gnome-screensaver
```

#### 配置修改 (main.py):

修改为你的服务器公网IP
```
server_ip = 'your.server.ip'
```

#### 运行客户端：

```
python3 main.py
```

### 三、手机控制端部署
将 index.html 部署到云服务器（端口：8821）

修改服务器地址（HTML 第537行），修改为你的服务器公网IP
```
ws = new WebSocket('ws://your.server.ip:8823');
```

## 📲 使用流程
启动云服务器、在目标电脑运行PC客户端、手机（或电脑）访问部署好的 index.html、点击"连接服务器"按钮

## 控制面板功能：
🖥️ 电脑控制：锁屏/关机

🔊 音量控制：静音/取消/滑块调节

> [!WARNING]
> 注意事项：确保防火墙开放以下端口：8821 (HTTP/HTTPS) 和 8822 (TCP) 和 8823 (WebSocket)

##  平台支持差异
|功能            |	Windows   |	macOS      |	Linux             |
| -------------- | ---------- | -----------|--------------------|
锁屏检测         |	✅	      |⚠️ 部分支持 |⚠️ 需要额外配置     |
音量控制	       |  ✅        |	✅	     |⚠️ 需要PulseAudio   |
远程关机	       |  ✅	      |   ✅       |	✅                |
状态实时推送     |	✅        |	✅       |	✅                |

## Linux 特殊配置：

#### Debian/Ubuntu
```
sudo apt-get install xflock4 gnome-screensaver pulseaudio
```

#### Arch Linux
```
sudo pacman -S xss-lock gnome-screensaver pulseaudio
```
## 多平台支持

- [x] Web网页
- [x] Windows 10
- [x] macOS 暂未实际测试
- [x] Linux 暂未实际测试
- [x] Android 
- [x] iOS 暂未实际测试

## TODO
- [ ] 锁屏检测 （半成品，用了点歪门邪道）
- [x] 锁屏
- [x] 关机
- [x] 静音
- [x] 取消静音
- [x] 滑块调节音量
- [ ] 解锁锁屏提醒
- [ ] 一键解锁锁屏 （在开发Windows方面遇到了点问题，还在学习，望有大佬能进行改进）
- [ ] 打开媒体播放音乐
- [ ] 等等...

## 贡献者

  <a href="https://github.com/lin080101/souldesk/" target="_blank">
    <img
      width="200"
      src="http://q.qlogo.cn/headimg_dl?dst_uin=2171204325&spec=640&img_type=jpg"
      alt="SoulDesk logo"
    />
  </a>
## 联系作者

### 一、添加QQ
  <a target="_blank">
    <img
      width="200"
      src="http://ff.soul6.cn/souldesk/qq.jpg"
      alt="Soul"
    />
  </a>
### 二、作者博客
  <a href="http://blog.soul6.cn/" target="_blank">
    <p>
      博客
    </p>
  </a>

## 初心

该项目初心只是作为作者学习的项目，而且希望能时刻看到电脑的状态，防止有人偷偷动作者的电脑。

## 愿景

各大远程软件虽然免费都能用，但免费版的功能覆盖不够全面。准确来说，作者想用的功能，暂且没有或者要money。所以爆肝开发此项目，程序是能正常运行，但有点幼稚...,没办法作者比较没有实力。望各位有实力的大佬可以一起改进和完善。谢谢大家的理解和支持！
