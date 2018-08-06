---
layout:     post
title:  Hadoop集群的无密码ssh登录设置  
category: blog
description: 构建hadoop集群，配置无密码ssh登录。
---
## ssh

在构建hadoop时，需要配置节点之间的ssh登录，因此通过ssh-keygen生成密钥，将公钥配置到其他节点下的\~/.ssh/authorised\_keys,就可以实现对其他节点的无密码登录。期间主要用到了三个命令。


1. ssh-keygen    #生成公钥和私钥

2. scp authorised_keys user@ip:/home/user/.ssh/  #在节点间传输文件

3. cat id_ras.pub \>\> authorised_keys   #将秘钥输出并且重定向到authorised_keys


## 策略

第一次采取分别各个机器上生成id\_rsa 和 id\#\_rsa.pub ,#为各个节点的id号，全部生成之后，将每台机器上的文件收集起来，写入到authorised\_keys中，之后分散给给个节点。后来发现这种方式过于繁琐。因此采用了另一种方式。


按照节点id号，顺序使用ssh-keygen命令生层密钥，选项都为默认选项，生成成功之后，将公钥写入到authorised\_keys中，将authorised\_keys传入到下一个节点的\~./ssh目录中，在下一台机器上继续上出操作，到最后一台机器上，将最终生成的authorised\_keys，传到之前的各台机器上覆盖同名文件。
之后每加一台新节点，都将新节点的公钥写入到authorised\_keys中，之后分发给各个节点。