HMonitor
=========

简介
-----

HMonitor是一个用于管理、丰富Zabbix监控的管理程序。在HMonitor和Zabbix的架构中，Zabbix
负责收集数据、定义trigger以及触发trigger对应的action给HMonitor。当HMonitor收到来自
Zabbix的告警后，其会根据告警的主机、告警内容等信息从自己的内容库中丰富这个告警，然后再从
自己的内容库中查看哪些用户订阅了这些告警，然后将告警通过邮件、短信等形式发送给订阅的用户。

安装
----

1. 在Zabbix中设置对应监控项，监控项的名称格式为：HM-告警简短描述。如HM-CPU_LOAD
2. 在Zabbix中设置对应的告警trigger，trigger的名称格式为：HM-trigger简短描述。如HM-CPU_HIGH_LOAD
3. 在Zabbix中设置script类型的媒体类型，设置HMonitor的脚本
4. 在Zabbix中设置对应的action