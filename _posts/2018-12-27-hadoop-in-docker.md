---
layout:     post
title:      容器中构建Hive,Spark以及Mysql设置
category: blog
description: 容器中,Hive,Spark,Mysql
tag: Hadoop ,linux，docker
---

# 数据库容器
承接上文，配置Hive的时候需要配置元数据存储，默认的是DERBY,由于通常使用的是Mysql，因此使用Mysql作为Hive元数据的存储数据库。元数据的存放有本地和远程两种模式。本地模式是指在于hive运行主机上安装数据库，直接通过localhost访问，远程模式是指使用远端的专门用于存储的主机，需要通过TCP链接。这里首先采用的远端模式。集群是通过容器搭建的，如果在运行hive的同时开启mysql后台运行的话需要配置--privilege 参数
	# docker pull centos
	# yum install mysql
	# service start mysql
	# yum install vsftpd
	Failed to get D-Bus connection: Operation not permitted

在容器中安装mysql,启动服务时会报错，无法获取D-Bus链接，这里的问题是在默认情况下，容器里面是不允许新开后台线程的。容器的设计理念是容器不运行后台服务，容器间基于相同的linux内核，容器可以看做是运行在宿主机上的一个独立的主进程，不同容器的区别可以说是这些主进程或者说容器内运行的应用进程不同。所以通常的做法是在容器里面运行前台进程。如果是在需要运行后台进程，就需要开启特权模式。需要改变容器的创建方式。

	docker run -d -name centos7 --privileged=true centos:7 /usr/sbin/init

`--privileged=true   `参数就指定容器以特权方式运行。之后就可以使用systemctl运行后台应用。当然也可以专门的Mysql容器.

`#dokcer pull mysql  `
