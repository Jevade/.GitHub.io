---
layout:     post
title:     类的一些基础知识
category: blog
description: 类，c++ ,python基础知识
tag:  类，c++ ,python
---

with STH as sth:
do some thing
使用这种方式，会调用 STH类的 `def _enter_`方法，将方法的返回值赋给sth,之后再结束的时候，会自动调用 `def _exit_ `方法，实现资源的释放等操作。所以当自己编写类的时候，如果要自己控制内存资源，可以使用这两个方法，在enter方法中使用资源开辟，在exit方法中释放资源，并且在遇到类的内部错误退出是，调用exit方法可以打印出出错的信息。
实际上，在with后面的代码块抛出异常时，exit()方法被执行。开发库时，清理资源，关闭文件等操作，都可以放在exit()方法中。
with 语句适用于对资源进行访问的场合，确保不管使用过程中是否发生异常都会执行必要的“清理”操作，释放资源

	`try:
	
	`    do sonething 
	
	`expect: 
	
	`     do something 
	
	`finally:
	
	`    do something 


with :
do somethong 1

mac上brew出错


	If you are facing an error like that on new MacOS version.
	xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun



longlybits
C++虚函数

1.简介 
虚函数是C++中用于实现多态(polymorphism)的机制。核心理念就是通过基类访问派生类定义的函数。假设我们有下面的类层次：

	class A
	{
	public:
	virtual void foo() { cout \<\< "A::foo() is called" \<\< endl;}
	};
	
	class B: public A
	{
	public:
	virtual void foo() { cout \<\< "B::foo() is called" \<\< endl;}
	};
	

那么，在使用的时候，我们可以：

A \* a = new B();
a-\>foo();       // 在这里，a虽然是指向A的指针，但是被调用的函数(foo)却是B的!

这个例子是虚函数的一个典型应用，通过这个例子，也许你就对虚函数有了一些概念。它虚就虚在所谓“推迟联编”或者“动态联编”上，一个类函数的调 用并不是在编译时刻被确定的，而是在运行时刻被确定的。由于编写代码的时候并不能确定被调用的是基类的函数还是哪个派生类的函数，所以被成为“虚”函数。

虚函数只能借助于指针或者引用来达到多态的效果，如果是下面这样的代码，则虽然是虚函数，但它不是多态的：

	class A
	{
	public:
	virtual void foo();
	};
	
	class B: public A
	{
	virtual void foo();
	};
	
	void bar()
	{
	A a;
	a.foo();   // A::foo()被调用
	}

1.1 多态 
在了解了虚函数的意思之后，再考虑什么是多态就很容易了。仍然针对上面的类层次，但是使用的方法变的复杂了一些：

void bar(A \* a)
{
a-\>foo();  // 被调用的是A::foo() 还是B::foo()？
}

因为foo()是个虚函数，所以在bar这个函数中，只根据这段代码，无从确定这里被调用的是A::foo()还是B::foo()，但是可以肯定的说：如果a指向的是A类的实例，则A::foo()被调用，如果a指向的是B类的实例，则B::foo()被调用。

这种同一代码可以产生不同效果的特点，被称为“多态”。

1.2 多态有什么用？ 
多态这么神奇，但是能用来做什么呢？这个命题我难以用一两句话概括，一般的C++教程（或者其它面向对象语言的教程）都用一个画图的例子来展示多 态的用途，我就不再重复这个例子了，如果你不知道这个例子，随便找本书应该都有介绍。我试图从一个抽象的角度描述一下，回头再结合那个画图的例子，也许你 就更容易理解。

在面向对象的编程中，首先会针对数据进行抽象（确定基类）和继承（确定派生类），构成类层次。这个类层次的使用者在使用它们的时候，如果仍然在需 要基类的时候写针对基类的代码，在需要派生类的时候写针对派生类的代码，就等于类层次完全暴露在使用者面前。如果这个类层次有任何的改变（增加了新类）， 都需要使用者“知道”（针对新类写代码）。这样就增加了类层次与其使用者之间的耦合，有人把这种情况列为程序中的“bad smell”之一。

多态可以使程序员脱离这种窘境。再回头看看1.1中的例子，bar()作为A-B这个类层次的使用者，它并不知道这个类层次中有多少个类，每个类 都叫什么，但是一样可以很好的工作，当有一个C类从A类派生出来后，bar()也不需要“知道”（修改）。这完全归功于多态--编译器针对虚函数产生了可 以在运行时刻确定被调用函数的代码。

1.3 如何“动态联编” 
编译器是如何针对虚函数产生可以再运行时刻确定被调用函数的代码呢？也就是说，虚函数实际上是如何被编译器处理的呢？Lippman在深度探索C++对象模型[1]()中的不同章节讲到了几种方式，这里把“标准的”方式简单介绍一下。

我所说的“标准”方式，也就是所谓的“VTABLE”机制。编译器发现一个类中有被声明为virtual的函数，就会为其搞一个虚函数表，也就是 VTABLE。VTABLE实际上是一个函数指针的数组，每个虚函数占用这个数组的一个slot。一个类只有一个VTABLE，不管它有多少个实例。派生 类有自己的VTABLE，但是派生类的VTABLE与基类的VTABLE有相同的函数排列顺序，同名的虚函数被放在两个数组的相同位置上。在创建类实例的 时候，编译器还会在每个实例的内存布局中增加一个vptr字段，该字段指向本类的VTABLE。通过这些手段，编译器在看到一个虚函数调用的时候，就会将 这个调用改写，针对1.1中的例子：

	void bar(A \* a)
	{
	a-\>foo();
	}

会被改写为：

	void bar(A \* a)
	{
	(a-\>vptr[1])();
	}
	
因为派生类和基类的foo()函数具有相同的VTABLE索引，而他们的vptr又指向不同的VTABLE，因此通过这样的方法可以在运行时刻决定调用哪个foo()函数。

虽然实际情况远非这么简单，但是基本原理大致如此。

1.4 overload和override 
虚函数总是在派生类中被改写，这种改写被称为“override”。我经常混淆“overload”和“override”这两个单词。但是随着各类C++的书越来越多，后来的程序员也许不会再犯我犯过的错误了。但是我打算澄清一下：

override是指派生类重写基类的虚函数，就象我们前面B类中重写了A类中的foo()函数。重写的函数必须有一致的参数表和返回值（C++标准允许 返回值不同的情况，这个我会在“语法”部分简单介绍，但是很少编译器支持这个feature）。这个单词好象一直没有什么合适的中文词汇来对应，有人译为 “覆盖”，还贴切一些。 
overload约定成俗的被翻译为“重载”。是指编写一个与已有函数同名但是参数表不同的函数。例如一个函数即可以接受整型数作为参数，也可以接受浮点数作为参数。 
2. 虚函数的语法 
	虚函数的标志是“virtual”关键字。

2.1 使用virtual关键字 
考虑下面的类层次：

	class A
	{
	public:
	virtual void foo();
	};
	
	class B: public A
	{
	public:
	void foo();    // 没有virtual关键字!
	};
	
	class C: public B  // 从B继承，不是从A继承！
	{
	public:
	void foo();    // 也没有virtual关键字！
	};

这种情况下，B::foo()是虚函数，C::foo()也同样是虚函数。因此，可以说，基类声明的虚函数，在派生类中也是虚函数，即使不再使用virtual关键字。

2.2 纯虚函数 
如下声明表示一个函数为纯虚函数：

	class A
	{
	public:
	virtual void foo()=0;   // =0标志一个虚函数为纯虚函数
	};

一个函数声明为纯虚后，纯虚函数的意思是：我是一个抽象类！不要把我实例化！纯虚函数用来规范派生类的行为，实际上就是所谓的“接口”。它告诉使用者，我的派生类都会有这个函数。

2.3 虚析构函数 
析构函数也可以是虚的，甚至是纯虚的。例如：

	class A
	{
	public:
	virtual A()=0;   // 纯虚析构函数
	};

当一个类打算被用作其它类的基类时，它的析构函数必须是虚的。考虑下面的例子：

	class A
	{
	public:
	A() { ptra\_ = new char[10];}
	A() { delete ptra;}        // 非虚析构函数
	private:
	char \* ptra\_;
	};
	
	class B: public A
	{
	public:
	B() { ptrb\_ = new char[20];}
	B() { delete ptrb;}
	private:
	char \* ptrb\_;
	};
	
	void foo()
	{
	A \* a = new B;
	delete a;
	}

在这个例子中，程序也许不会象你想象的那样运行，在执行delete a的时候，实际上只有A::A()被调用了，而B类的析构函数并没有被调用！这是否有点儿可怕？

如果将上面A::A()改为virtual，就可以保证B::B()也在delete a的时候被调用了。因此基类的析构函数都必须是virtual的。

纯虚的析构函数并没有什么作用，是虚的就够了。通常只有在希望将一个类变成抽象类（不能实例化的类），而这个类又没有合适的函数可以被纯虚化的时候，可以使用纯虚的析构函数来达到目的。

2.4 虚构造函数？ 
构造函数不能是虚的。

3. 虚函数使用技巧 3.1 private的虚函数 
	考虑下面的例子：
	
	class A
	{
	public:
	void foo() { bar();}
	private:
	virtual void bar() { ...}
	};
	
	class B: public A
	{
	private:
	virtual void bar() { ...}
	};

在这个例子中，虽然bar()在A类中是private的，但是仍然可以出现在派生类中，并仍然可以与public或者protected的虚函 数一样产生多态的效果。并不会因为它是private的，就发生A::foo()不能访问B::bar()的情况，也不会发生B::bar()对 A::bar()的override不起作用的情况。

这种写法的语意是：A告诉B，你最好override我的bar()函数，但是你不要管它如何使用，也不要自己调用这个函数。

3.2 构造函数和析构函数中的虚函数调用 
一个类的虚函数在它自己的构造函数和析构函数中被调用的时候，它们就变成普通函数了，不“虚”了。也就是说不能在构造函数和析构函数中让自己“多态”。例如：

	class A
	{
	public:
	A() { foo();}        // 在这里，无论如何都是A::foo()被调用！
	A() { foo();}       // 同上
	virtual void foo();
	};
	
	class B: public A
	{
	public:
	virtual void foo();
	};
	
	void bar()
	{
	A \* a = new B;
	delete a;
	}

如果你希望delete a的时候，会导致B::foo()被调用，那么你就错了。同样，在new B的时候，A的构造函数被调用，但是在A的构造函数中，被调用的是A::foo()而不是B::foo()。

3.3 多继承中的虚函数 3.4 什么时候使用虚函数 
在你设计一个基类的时候，如果发现一个函数需要在派生类里有不同的表现，那么它就应该是虚的。从设计的角度讲，出现在基类中的虚函数是接口，出现在派生类中的虚函数是接口的具体实现。通过这样的方法，就可以将对象的行为抽象化。

以设计模式[2]()中Factory Method模式为例，Creator的factoryMethod()就是虚函数，派生类override这个函数后，产生不同的Product类，被 产生的Product类被基类的AnOperation()函数使用。基类的AnOperation()函数针对Product类进行操作，当然 Product类一定也有多态（虚函数）。

另外一个例子就是集合操作，假设你有一个以A类为基类的类层次，又用了一个std::vector\<A \*\>来保存这个类层次中不同类的实例指针，那么你一定希望在对这个集合中的类进行操作的时候，不要把每个指针再cast回到它原来的类型（派生 类），而是希望对他们进行同样的操作。那么就应该将这个“一样的操作”声明为virtual。

现实中，远不只我举的这两个例子，但是大的原则都是我前面说到的“如果发现一个函数需要在派生类里有不同的表现，那么它就应该是虚的”。这句话也可以反过来说：“如果你发现基类提供了虚函数，那么你最好override它”。

4.参考资料 
[1]() 深度探索C++对象模型，Stanley B.Lippman，侯捷译

[2]() Design Patterns, Elements of Reusable Object-Oriented Software, GOF

It means that you need to install XCode command line, open a Terminal and run this command:



$ xcode-select --install



