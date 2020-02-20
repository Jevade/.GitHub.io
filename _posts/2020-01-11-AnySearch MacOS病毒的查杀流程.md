---
layout: post
title:   AnySearch MacOS病毒的查杀流程 
category: blog
description: AnySearch ，Mac OS，病毒，浏览器
tag: AnySearch ，Mac OS，病毒，浏览器
---
新年伊始，跟了我两三年的macbook pro开始出现各种问题，卡顿闪退，内存爆满，最后连VS Code打开都卡卡顿顿，时不时来个无服务。然后chrome浏览器的默认搜索都变成一个Any Search的奇葩东西，我要的是我的duckduckgo,要你这2B玩意儿干啥，反复修改了好几次默认搜索引擎，没过多久又死灰复燃，然后Chrome浏览器设置最下一行，出现“由贵单位管理”。我的浏览器被劫持了。。。。。
网上一搜，发现还挺多这种问题的，是AnySearch的变种，我这里叫做MajorLetterSearch。
流程
杀死进程
使用电脑的活动监视器，搜索search,发现了病毒的Deamon进程和子进程，直接点停止运行，发现杀不死这玩意儿。开终端，切到root用户，搜索相关进程。 

	sh-3.2# ps -ef|grep MajorLetterSearc
	0 70679     1   0  4:26PM ??         0:01.98 /var/root/.MajorLetterSearch/MajorLetterSearchDaemon
	0 70692 70679   0  4:26PM ??         0:00.00 (MajorLetterSearc)
	0 70811 70679   0  4:26PM ??         0:00.00 (MajorLetterSearc)
	0 70998 70679   0  4:27PM ??         0:00.00 (MajorLetterSearc)
	0 71265 70679   0  4:27PM ??         0:00.00 (MajorLetterSearc)
	0 71506 70679   0  4:28PM ??         0:00.00 (MajorLetterSearc)
	0 71686 70679   0  4:28PM ??         0:00.00 (MajorLetterSearc)
	0 71868 70679   0  4:28PM ??         0:00.00 (MajorLetterSearc)
	0 72051 70679   0  4:29PM ??         0:00.00 (MajorLetterSearc)
	0 72170 71290   0  4:29PM ttys001    0:00.00 grep MajorLetterSearc
	sh-3.2# kill -9 70679 70692 70811 70998 71265 71506 71686 71868 72051 72170


重新搜索，发现没有在运行了

	sh-3.2# ps -ef|grep MajorLetterSearc
	0 72502 71290   0  4:30PM ttys001    0:00.00 grep MajorLetterSearc
	
查看病毒执行文件目录，藏得还很隐蔽

	sh-3.2# ls  /var/root/.MajorLetterSearch/MajorLetterSearch
	MajorLetterSearch     MajorLetterSearch.py

取消病毒文件的执行权限


	sh-3.2# chmod -x   /var/root/.MajorLetterSearch/*	
	sh-3.2# ls -al  /var/root/.MajorLetterSearch/*
	-rw-------  1 root  wheel  12096424 Jan 11 16:28 /var/root/.MajorLetterSearch/MajorLetterSearch
	-rw-------  1 root  wheel      9592 Jan 11 16:28 /var/root/.MajorLetterSearch/MajorLetterSearch.py


把病毒文件复制打包保存，然后删除原始病毒文件


	sh-3.2# tar -cvf  MajorLetterSearch.tar /var/root/.MajorLetterSearch
	tar: Removing leading '/' from member names
	a var/root/.MajorLetterSearch
	a var/root/.MajorLetterSearch/MajorLetterSearch
	a var/root/.MajorLetterSearch/MajorLetterSearch.py
	sh-3.2# ls MajorLetterSearch.tar
	MajorLetterSearch.tar
	sh-3.2# rm -rf /var/root/.MajorLetterSearch

然后删除相关的配置文件，使用find全盘查找病毒相关文件


	sh-3.2# find / -name  MajorLetterSearch
	/Library/Application Support/com.MajorLetterSearchDaemon/MajorLetterSearch
	find: /System/Volumes/Data/.Spotlight-V100: No such file or directory
	find: /System/Volumes/Data/.PKInstallSandboxManager-SystemSoftware: No such file or directory
	/System/Volumes/Data/Library/Application Support/com.MajorLetterSearchDaemon/MajorLetterSearch
	find: /System/Volumes/Data/mnt: No such file or directory
	find: /System/Volumes/Data/.DocumentRevisions-V100: No such file or directory
	/System/Volumes/Data/Users/liu/Library/Application Support/com.MajorLetterSearch/MajorLetterSearch
	^@find: /System/Volumes/Data/.TemporaryItems: No such file or directory
	find: /System/DriverKit: No such file or directory
	/Users/liu/Library/Application Support/com.MajorLetterSearch/MajorLetterSearch
	^@find: /dev/fd/3: Not a directory
	find: /dev/fd/4: Not a directory

按照找出的结果，使用rm -rf 逐个删除就行了，删除完重新搜索一遍，避免遗漏。

之后浏览器就正常了。





