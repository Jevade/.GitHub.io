---
layout:     post
title:      容器中构建Hive,Spark以及Mysql设置
category: blog
description: 容器中,Hive,Spark,Mysql
tag: Hadoop ,linux，docker
---

# 数据库容器及Hive元数据存储配置
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

	docker run -itd  —name mysql -h hostname   —ip=ip   —add-host   master:172.18.0.3 -net=mysubnet   -p 3306:3306  mysql


-name mysql 

定义了容器的名称，使用docker ps的时候，会显示container的名字是mysql

`-h hostname
`
定义了容易的HOSTNAME

`--ip=MYSTATICIP
`
定义了容器的静态IP地址，此时必需使用自定义网络

docker中关于自定义网络的命令有：

	docker network create —subnet=172.18.0.0/16 mySunNet
	docker network rmmySubNet

宿主机与容器的端口映射，
将容器的3306端口映射到宿主机的3396端口，之后通过 可以通过宿主机ip链接mysql容器，适合在mysql容器和hive容器不在同一docker network的时候。

	-p 3306:3306

之后需要设置数据库的远程连接，直接修改数据库mysql.user中对应用户的信息

	GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '123456' WITH GRANT OPTION;
	FLUSH RIVILEGES

mysql 版本是8.0.13
![][image-1]

之后使用远程连接时报错

	error 2059: Authentication plugin 'caching_sha2_password' cannot be loaded: /usr/lib64/mysql/plugin/caching_sha2_password.so: cannot open shared object file: No such file or directory

这是因为最新版mysql-8.0.13默认的认证方式是`caching_sha2_password` ，而在MySQL5.7版本则为`mysql_native_password`。

解决这个问题有两种方法
1. 配置my.cnf并重启，并重启.

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

查询目录下存在的所有文件 。

	find  /  -name hive-site.xml|xargs cat|grep -A 1 -n mysql

查询所有` hive-site.xml `文件中存在的包含mysql的行，并显示所在行后一行和所在行号。
![][image-2]
![][image-3]

	[root@pbs1 ~]# find / -name hive-site.xml|xargs cat |grep -B 1 -A 1 -n mysql
	550-    <name>javax.jdo.option.ConnectionURL</name>
	551:    <value>jdbc:mysql://10.90.226.189:3306/hive?createDatabaseIfNotExist=true</value>
	552-    <description>
	--
	1025-    <name>javax.jdo.option.ConnectionDriverName</name>
	1026:    <value>com.mysql.jdbc.Driver</value>
	1027-    <description>Driver class name for a JDBC metastore</description>
	--
	3221-    <name>hive.druid.metadata.db.type</name>
	3222:    <value>mysql</value>
	3223-    <description>
	3224:      Expects one of the pattern in [mysql, postgresql].
	3225-      Type of the metadata database.
	--
	3240-    <value/>
	3241:    <description>URI to connect to the database (for example jdbc:mysql://hostname:port/DBName).</description>
	3242-  </property>
	--
	6510-    <name>javax.jdo.option.ConnectionURL</name>
	6511:    <value>jdbc:mysql://10.90.226.189:3306/hive?createDatabaseIfNotExist=true</value>
	6512-    <description>
	--
	6985-    <name>javax.jdo.option.ConnectionDriverName</name>
	6986:    <value>com.mysql.jdbc.Driver</value>
	6987-    <description>Driver class name for a JDBC metastore</description>
	--
	9181-    <name>hive.druid.metadata.db.type</name>
	9182:    <value>mysql</value>
	9183-    <description>
	9184:      Expects one of the pattern in [mysql, postgresql].
	9185-      Type of the metadata database.
	--
	9200-    <value/>
	9201:    <description>URI to connect to the database (for example jdbc:mysql://hostname:port/DBName).</description>
	9202-  </property>
	--
	12470-    <name>javax.jdo.option.ConnectionURL</name>
	12471:    <value>jdbc:mysql://10.90.226.189:3306/hive?createDatabaseIfNotExist=true</value>
	12472-    <description>
	--
	12945-    <name>javax.jdo.option.ConnectionDriverName</name>
	12946:    <value>com.mysql.jdbc.Driver</value>
	12947-    <description>Driver class name for a JDBC metastore</description>
	--
	15141-    <name>hive.druid.metadata.db.type</name>
	15142:    <value>mysql</value>
	15143-    <description>
	15144:      Expects one of the pattern in [mysql, postgresql].
	15145-      Type of the metadata database.
	--
	15160-    <value/>
	15161:    <description>URI to connect to the database (for example jdbc:mysql://hostname:port/DBName).</description>
	15162-  </property>之后可以用sed命令替换文件中的相应字符。
sed 替换

`sed -i   s/oristr/newstr/g
`
替换字符部分使用单引号之后，系统不会进行对应的替换，直接当做字符处理，使用双引号，或者不用引号，会进行替换，所以对于特殊字符需要进行转义。
-i 选项对直接操作源文件，不带的话会将替换结果打印到屏幕上。
[^1]

下载对应的mysql驱动包，放到hive和spark的lib文件家中，之后连接的时候会自动加载驱动。


	[root@pbs1 ~]# wget https://************/mysql-connector-java-8.0.13.tar.gz`
	[root@pbs1 ~]# tar xvzf mysql-connector-java-8.0.13.tar.gz
	[root@pbs1 ~]# ls mysql-connector-java-8.0.13/
	build.xml  CHANGES  derby.log  lib  LICENSE  metastore_db  mysql-connector-java-8.0.13.jar  README  src
	[root@pbs1 ~]# ls ./apache-hive-2.3.0-bin/lib/mysql-connector-java-8.0.13.jar
	./apache-hive-2.3.0-bin/lib/mysql-connector-java-8.0.13.jar


# 修改hive任务记录的默认文件夹

	[root@pbs1 ~]# find / -name hive-site.xml|xargs cat |grep -B 1 -A 1 -n '/root/tmp/'
	74-    <name>hive.exec.local.scratchdir</name>
	75:    <value>/root/tmp/${system:user.name}</value>
	76-    <description>Local scratch space for Hive jobs</description>
	--
	79-    <name>hive.downloaded.resources.dir</name>
	80:    <value>/root/tmp/${hive.session.id}_resources</value>
	81-    <description>Temporary local directory for added resources in the remote file system.</description>
	--
	1690-    <name>hive.querylog.location</name>
	1691:    <value>/root/tmp/${system:user.name}</value>
	1692-    <description>Location of Hive run time structured log file</description>
	--
	3976-    <name>hive.server2.logging.operation.log.location</name>
	3977:    <value>/root/tmp/${system:user.name}/operation_logs</value>
	3978-    <description>Top level directory where operation logs are stored if logging functionality is enabled</description>
	--
	6034-    <name>hive.exec.local.scratchdir</name>
	6035:    <value>/root/tmp/root</value>
	6036-    <description>Local scratch space for Hive jobs</description>
	--
	6039-    <name>hive.downloaded.resources.dir</name>
	6040:    <value>/root/tmp/${hive.session.id}_resources</value>
	6041-    <description>Temporary local directory for added resources in the remote file system.</description>
	--
	7650-    <name>hive.querylog.location</name>
	7651:    <value>/root/tmp/root</value>
	7652-    <description>Location of Hive run time structured log file</description>
	--
	9936-    <name>hive.server2.logging.operation.log.location</name>
	9937:    <value>/root/tmp/root/operation_logs</value>
	9938-    <description>Top level directory where operation logs are stored if logging functionality is enabled</description>
	--
	11994-    <name>hive.exec.local.scratchdir</name>
	11995:    <value>/root/tmp/${system:user.name}</value>
	11996-    <description>Local scratch space for Hive jobs</description>
	--
	11999-    <name>hive.downloaded.resources.dir</name>
	12000:    <value>/root/tmp/${hive.session.id}_resources</value>
	12001-    <description>Temporary local directory for added resources in the remote file system.</description>
	--
	13610-    <name>hive.querylog.location</name>
	13611:    <value>/root/tmp/${system:user.name}</value>
	13612-    <description>Location of Hive run time structured log file</description>
	--
	15896-    <name>hive.server2.logging.operation.log.location</name>
	15897:    <value>/root/tmp/${system:user.name}/operation_logs</value>
	15898-    <description>Top level directory where operation logs are stored if logging functionality is enabled</description>
	[root@pbs1 ~]##


这个默认路径写的是`"${system.java.io} ` 如果不修改的话，运行会报错，并且运行文件夹会生成一个文件。`${system:java.io.tmpdir}`


	[root@pbs1 ~]# ls
	1.txt                  derby.log     jdk1.8.0_144                 mysql-connector-java-8.0.13.tar.gz  sogou-log-filter.sh        ${system:java.io.tmpdir}
	anaconda-ks.cfg        hadoop-2.7.3  metastore_db                 scala-2.12.1                        spark-2.1.0-bin-hadoop2.7  tmp
	apache-hive-2.3.0-bin  id_rsa.pub.2  metastore.log                scala-2.12.1.tgz                    spark-2.4.0-bin-hadoop2.7  weibo
	apache-hive-3.1.1-bin  id_rsa.pub.3  mysql-connector-java-8.0.13  sogou.500w.utf8.flt                 spark-warehouse
	[root@pbs1 ~]#

如果发现存在这个文件表明这一项没有配置好，我这里是`/root/tmp`,要生成这个文件夹，并设置权限。

	mkdir -p  /root/tmp
	chmod  -R 755 /root/tmp

# 通过SSH连接局域网内windows主机上的安装的docker容器实例

由于服务器是安装的Windows,所以在构建容器的时候讲宿主机的端口映射到容器的22端口，在容器内安装openssh,运行sshd,通常在命令行手动运行sshd 需要指明全路径。

	[root@pbs1 ~]# which sshd
	/usr/sbin/sshd
	[root@pbs1 ~]# /usr/sbin/sshd

容器构建的时候

	docker run -itd  --name mysql -h hostname   --ip=MyIP   --add-host   master:172.18.0.3 -net=mysubnet   -p 1092:22  hadoop 

将容器的22端口映射到宿主机的1092端口，就可以使用ssh远程连接容器

	ssh  root@10.90.226.189 -p 1092`
	`➜  ~ ssh  root@10.90.226.189 -p 1092
	root@10.90.226.189's password:
	Last login: Thu Dec 27 10:10:20 2018 from 172.18.0.1
	-bash-4.2# bash
	[root@pbs1 ~]#

[^1]:	.

[image-1]:	https://www.dropbox.com/s/pry0fy3vqljt96c/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202018-12-27%2017.16.10.png?dl=0
[image-2]:	https://www.dropbox.com/s/uhe678qdwkjmm43/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202018-12-27%2017.41.41.png?dl=0
[image-3]:	https://www.dropbox.com/s/o9nj1tteck4sffd/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202018-12-27%2017.55.32.png?dl=0