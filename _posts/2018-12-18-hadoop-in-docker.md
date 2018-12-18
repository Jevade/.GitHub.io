---
layout:     post
title:      hadoop，docker
category: blog
description: 容器中构建hadoop分布式环境
tag:hadoop ,linux，docker
---
# 容器中构建hadoop分布式环境

最近需要学习大数据实践，任课老师用的是基于VMware搭建多个虚拟机来实现的，虽然使用虚拟机可以只用链接克隆的方式搭建多个节点，但是对于我的乞丐版macbook来说，虚拟机还是大了，随便一个就需要2,30G的存储空间，而且多个虚拟机跑起来，风扇转的声音过于大了。因此考虑使用容器来构建多节点环境。

首先下载hadoop容器,在docker-hub搜索，下载量最大的是sequenceiq/hadoop-docker ，使用的hadoop是2.7.0版本：
`docker pull sequenceiq/hadoop-docker
`
如果需要定制运行环境的话可以下载基础的linux环境，自行安装所需的软件，打包成镜像使用。

容器中 /etc/hosts这些文件是易失的，并且每次重启之后容器的ip地址为自动分配，配置hadoop集群需要配置节点间的无密码登录，所以最好采用固定ip的方式。容器使用默认的网络的话是不能自定义ip地址的，所以需要自定义网络。

查看已有的网络
	docker network ls

删除网络
	docker network rm mynetwork
	

删除未使用网络
	docker network prune

查看网络详情
 
	$docker network inspect mynetwork
	[
	    {
	        "Name": "mynetwork",
	        "Id": "19b78ca1706bbee61a4e14157abd9274e2d18bc317fe2212166813ea18521984",
	        "Created": "2018-12-18T10:15:06.4521877Z",
	        "Scope": "local",
	        "Driver": "bridge",
	        "EnableIPv6": false,
	        "IPAM": {
	            "Driver": "default",
	            "Options": {},
	            "Config": [
	                {
	                    "Subnet": "172.18.0.0/16"
	                }
	            ]
	        },
	        "Internal": false,
	        "Attachable": false,
	        "Ingress": false,
	        "ConfigFrom": {
	            "Network": ""
	        },
	        "ConfigOnly": false,
	        "Containers": {
	            "25abf62fe6a913d3b362e057172a4d4a759130f7f64a333f0e553467de2d9218": {
	                "Name": "pbs1",
	                "EndpointID": "a513f45550fae124dcde1a976bebe533a9fd6cda325fdca6fe870816f9cbb66d",
	                "MacAddress": "02:42:ac:12:00:03",
	                "IPv4Address": "172.18.0.3/16",
	                "IPv6Address": ""
	            },
	            "5d3ed688687f5351a133b3a56c133579621f54f925622ccc659a3a7177e59479": {
	                "Name": "pbs3",
	                "EndpointID": "2982f006411d33176761000972b8cbd3bfc75a75d926e96cd93a87a54795ec92",
	                "MacAddress": "02:42:ac:12:00:05",
	                "IPv4Address": "172.18.0.5/16",
	                "IPv6Address": ""
	            },
	            "7d4fe969edb91e2dfab4dfca7dfbc3e2f6c2ef9226128c8759364d43f9cc325d": {
	                "Name": "mySubNginx",
	                "EndpointID": "8c867a147aa9af49f9d1e97e86914a65fec8ef0c82b9bdefff21db797dfd3e15",
	                "MacAddress": "02:42:ac:12:00:06",
	                "IPv4Address": "172.18.0.6/16",
	                "IPv6Address": ""
	            },
	            "8ce4135ef91109560a2ef538a313d147861092f8687023dd252ed2bd1d8ca8d0": {
	                "Name": "pbs2",
	                "EndpointID": "5c29e52b2c939f49480398ffbd9a05f1b4f2676a4feedce3974fa8820913f0d8",
	                "MacAddress": "02:42:ac:12:00:04",
	                "IPv4Address": "172.18.0.4/16",
	                "IPv6Address": ""
	            }
	        },
	        "Options": {},
	        "Labels": {}
	    }
	]

可以看到自定义的网络下面已经有三个容器了，这是已经定义好的，将定义容器的语句写到脚本中。
	docker run -tid --name pbs1 -h pbs1 --add-host pbs1:172.18.0.3 --add-host pbs2:172.18.0.4 --add-host pbs3:172.18.0.5 --net=mynetwork --ip=172.18.0.3 myhadoop
	
	docker run -tid --name pbs2 -h pbs2 --add-host pbs1:172.18.0.3 --add-host pbs2:172.18.0.4 --add-host pbs3:172.18.0.5 --net=mynetwork --ip=172.18.0.4 myhadoop
	
	docker run -tid --name pbs3 -h pbs3 --add-host pbs1:172.18.0.3 --add-host pbs2:172.18.0.4 --add-host pbs3:172.18.0.5 --net=mynetwork --ip=172.18.0.5 myhadoop
	docker run -tid --name mySubNginx -h mySubNginx --add-host pbs1:172.18.0.3 --add-host pbs2:172.18.0.4 --add-host pbs3:172.18.0.5 --net=mynetwork --ip=172.18.0.6 -d -p 1090:80 -v  /Users/liu/docker/myNginx/conf.d:/etc/nginx/conf.d  nginx

定义了三个hadoop容器和一个nginx容易，通过nginx反向代理访问hadoop的管理界面。

docker run 可以带参数，从而可以定义容易的属性
	docker run -tid 
	--name pbs3 # 定义容器名称
	-h pbs3 #定义容器的host
	--add-host pbs1:172.18.0.3  #定义容器的hosts文件
	--add-host pbs2:172.18.0.4 
	--add-host pbs3:172.18.0.5 
	--net=mynetwork #定义容器使用的网络
	--ip=172.18.0.5 #定义容器的ip
	myhadoop#容器使用的镜像

docker cp 可以在宿主和容器之间转递文件,格式为：
	docker cp -r SRC-PATH container:DEST-PATH

容器之间可以通过scp传递文件
	scp -r [container1:]SRC-PATH [container2:]DEST-PATH 

容器配置好之后可以保存为新的镜像
	docker commit containerID name

删除容器
	docker rm  containerID

删除镜像
	docker rmi  imageID

启动容器
	docker start containerID

进入容器，并且推出容器不停止
	docker exec -it containerID|containerName  /bin/bash 

Run a command in a running container
	docker exec [OPTIONS] CONTAINER COMMAND [ARG…]

除了使用命令行构造容器容器外，还可以使用配置文件构造容器，**docker-compose.yml**，使用docker-compose up -d命令，构建容器

	version: '2'
	services:
	  a0:
	    image: myhadoop
	    container_name: a0
	    ports:
	      - "19010:22"#端口映射
	    restart: always
	  a1:
	    image: myhadoop
	    container_name: a1
	    depends_on:#确定依赖项，从而确定启动顺序
	      - a0
	    ports:
	      - "19011:22"
	    restart: always
	  a2:
	    image: myhadoop
	    container_name: a2
	    depends_on:
	      - a1
	    ports:
	      - "19012:22"
	    restart: always

使用这种方法构建容器，容器会一直restarting,这个可能类似于  docker exec -it  ….中使用 -it 的情况，没有深入了解

还可以构造dockerfile来定义容器，这些内容以后再了解。

