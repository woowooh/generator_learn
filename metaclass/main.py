#1. instance 是 class 的实例， class 是metaclass的实例
#2. class (cls) 可通过 type() 方法创建类 api 为
#
#	type(类名, 父类(元祖类型).可以为空, 包含属性的字典(名称和值))


# example

class MyShinyClass(object):
    pass


# 等同于: 

MyShinyClass = type('MyShinyClass', (), {})


# 1. 构建 Foo 类
class Foo(object):
    bar = True

Foo = type('Foo', (), {'bar': True})

# 总结理解: 第一个参数为生成类的名字，通过 Foo.__name__ 可以获取，第二个参数为继承的父类， 第三个参数为 类属性字典。

# 为 类实例添加方法

def echo_bar(self):
    print(self.bar)

Foo = type('Foo', (), {'echo_bar': echo_bar})
foo = Foo()
foo.echo_bar()


############################

# __new__ 方法实现单例:

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

s1 = Singleton()
s2 = Singleton()

print(s1 is s2)


# 元类实现单例

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super(Singleton, self).__init__(*args, **kwargs)

     def __call__(self, *args, **kwargs):
         if self.__instance is None:
             self.__instance = super(Singleton, self).__call__(*args, **kwargs)
         return self.__instance

无 metaclass， 调用 type 方法创建类，有则调用 元类 __call__？

class Foo(object):
    __metaclass__ = Singleton


foo1 = Foo()
foo2 = Foo()

print(foo1 is foo2)


总结:

1. __new__ 用来在构造新对象之前调用。new 一个对象返回
2. 元类的对象会被反复调用，所以要实现个__call__方法, init 用来决定控制逻辑？？
https://www.cnblogs.com/tkqasn/p/6524879.html
