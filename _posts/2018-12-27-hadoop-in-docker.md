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
镜像拉下来之后，运行容器。
```docker run -itd  --name mysql -h hostname   --ip=ip   --add-host   master:172.18.0.3 -net=mysubnet   -p mysql`

`-name mysql 
`
定义了容器的名称，使用docker ps的时候，会显示container的名字是mysql

`-h hostname
`
定义了容易的HOSTNAME

`--ip=MYSTATICIP
`
定义了容器的静态IP地址，此时必需使用自定义网络

docker中关于自定义网络的命令有：
```docker network create --subnet=172.18.0.0/16 mySunNet
````docker network rmmySubNet`


之后需要设置数据库的远程连接，直接修改数据库mysql.user中对应用户的信息

```GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '123456' WITH GRANT OPTION;`
```FLUSH RIVILEGES`

mysql 版本是8.0.13
![][image-1]

之后使用远程连接时报错，
	`error 2059: Authentication plugin 'caching_sha2_password' cannot be loaded: /usr/lib64/mysql/plugin/caching_sha2_password.so: cannot open shared object file: No such file or directory

这是因为最新版mysql-8.0.13默认的认证方式是`caching_sha2_password` ，而在MySQL5.7版本则为`mysql_native_password`。

解决这个问题有两种方法
1. 配置my.cnf并重启，并重启
	vim my.cnf
	[mysqld]
	default_authentication_plugin=mysql_native_password
	
2. 改变对应用户的密码加密规则
	ALTER USER 'root'@'localhost' IDENTIFIED BY 'root' PASSWORD EXPIRE NEVER; #修改加密规则 
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'; #更新一下用户的密码 
	FLUSH PRIVILEGES; #刷新权限
		--创建新的用户：
		create user root@'%' identified WITH mysql_native_password BY 'root';
		grant all privileges on *.* to root@'%' with grant option;
		flush privileges;
		--在MySQL8.0创建用户并授权的语句则不被支持：
		mysql> grant all privileges on *.* to root@'%' identified by 'root' with grant option;
	        ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'identified by 'root' with grant option' at line 1
	
之后需要修改Hive,spark中的hive-site.xml文件，新下载的软件包中通常没有这个文件，有hive-site.xml.template 文件，可以修改为hive-site.xml，在其中添加配置项目。
	hive-site.xml
查询目录下存在的所有文件 
![][image-2]
![][image-3]
文件中显示了设置
sed 替换
`sed -i   s/oristr/newstr/g
`使用单引号之后
 [^1]

[^1]:	.

[image-1]:	https://www.dropbox.com/s/pry0fy3vqljt96c/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202018-12-27%2017.16.10.png?dl=0
[image-2]:	https://www.dropbox.com/s/uhe678qdwkjmm43/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202018-12-27%2017.41.41.png?dl=0
[image-3]:	https://www.dropbox.com/s/o9nj1tteck4sffd/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202018-12-27%2017.55.32.png?dl=0