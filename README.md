# HMonitor

## 简介

HMonitor是一个用于从Zabbix处接收告警后，进行告警管理、告警自动化处理等功能的一个工具平台。目前提供的功能包括：

1. 查看告警事件。使用者可以在“事件查看”标签下查看自己订阅的告警以及所有告警，并且了解有哪些告警需要自己处理
2. 告警通知的订阅管理。在“订阅管理”标签下使用者可以订阅告警，对告警进行屏蔽，并查看一段时间内的告警情况
3. 告警的自动修复。在“自动修复”标签下使用者可以查看目前提供的自动修复脚本，并且可以将告警事件和对应的修复脚本绑定，绑定后后续的告警会首先由修复脚本尝试修复，修复失败后才会告警。同时在该标签页下可以查看修复的成功率以及修复失败的原因。

## 系统架构

![image](https://github.com/QthCN/hmonitor/blob/master/docs/images/framework.jpg)

## 安装

1. 在Zabbix处配置script类型的媒体类型，脚本设置为HMonitor源码目录下的scripts/zabbix_hm.py
2. 配置trigger，trigger名需要以HM-打头
3. 配置相应的接收告警用户，用户的send to配置为HMonitor的地址
4. 在某台主机安装MySQL
5. 执行HMonitor源码目录下的db.sql建立对应的表
6. 执行hmonitor.py即可运行HMonitor/AutoFixer
7. 执行hmonitor_agent.py即可运行HMonitor Agent

HMonitor/AutoFixer属于无状态服务，如果集群中告警或需要自动处理的主机较多，可以启动多个HMonitor/AutoFixer并将他们放在如nginx之类的LB后面。

## 使用

### 订阅管理

点击*订阅告警*，即可查看所有可以被订阅的告警。如果对某个告警赶兴趣则可以在操作栏下点击*订阅告警*，如果不想再次接收这个告警则可以点击*取消订阅*。

![image](https://github.com/QthCN/hmonitor/blob/master/docs/images/subscribe_alerts.jpg)

订阅告警后，可以在*我的订阅*下面查看自己订阅的告警。不同级别的告警被不同颜色标记。

![image](https://github.com/QthCN/hmonitor/blob/master/docs/images/view_alerts.jpg)

如果某端时间某个主机在做类似扩容的操作，期间会触发很多IO wait的告警，则可以在这段时间内屏蔽这些告警。屏蔽告警可以在*告警屏蔽*中进行。

![image](https://github.com/QthCN/hmonitor/blob/master/docs/images/filter_alerts.jpg)

另外，可以在*告警统计*下查看最近一段时间的告警发送情况。

![image](https://github.com/QthCN/hmonitor/blob/master/docs/images/show_alerts.jpg)

