#!/usr/bin/env python
# -- coding: UTF-8 --
import os, sys, time, getpass
import json
import collections

reload(sys)
sys.setdefaultencoding('utf8')

# key className
Result = collections.namedtuple("Result", ["key","define", "name"])
# 解析所有结果 [Result]
keyItems = []
# 所有类名
classNames = []
# 解析结果 [String]
resContents = []

# 模型的解析类型
inParser = ""
# 继承关系
inInherit = "NSObject"
# 文件名前缀
inPrefix = "SJ"
# 解析的最外层类名
inClcName = "JsonResult"
# 类型: struct class
inType = "class"
# 修饰符
inModifier = "public"
# 语言： oc - swift
inLanguage = "Swift"


# 文件描述
def header():
    now = time.strftime('%Y',time.localtime(time.time()))
    detail = time.strftime('%Y/%m/%d',time.localtime(time.time()))
    user = getpass.getuser()
    header = '''//
//  {0}.{1}
//  Json2Swift
//
//  Created by {2} on {3}.
//  Copyright © {4}年 HH. All rights reserved.
//
	'''.format(classNames[0], postfix(), user, detail, now)

    if inLanguage == "Objective-C":
        header += "\n#import <Foundation/Foundation.h>\n"

    return header

# objectMapper 适用代码
def addMapper(cls):
    preModifier = "required "
    preFunc = ""
    if (inType == "struct"):
        preModifier = ""
        preFunc = "mutating "
    
    initial = "\n    {} init?(map: Map) ".format(preModifier + inModifier)
    initial += "{}\n"
    mapping = "\n    {} func mapping(map: Map) ".format(preFunc + inModifier)
    mapping += "{"
    resContents.append(initial + mapping)
    for r in keyItems:
        if r.name == cls:
            resContents.append('        {0}   <-   map["{0}"]'.format(r.key))
    resContents.append("    }")

# 特殊结构
def addStructure(cls):
    if inParser == "objectMapper":
        addMapper(cls)

# 父类
def parentCls():
    if inParser == "objectMapper":
        mapper = ": Mappable"
        if len(inInherit) > 0:
            mapper += ", {}".format(inInherit)
        return mapper

    if len(inInherit) > 0:
        return ": {}".format(inInherit)
    return ""
    
# 转换成swift对应类型
def convetType(value, key):
    if isinstance(value, str):
        return "String" if (inLanguage == "Swift") else "NSString *"
    elif isinstance(value, float):
        return "Float" if (inLanguage == "Swift") else "double "
    elif isinstance(value, bool):
        return "Bool" if (inLanguage == "Swift") else "BOOL "
    elif isinstance(value, int):
        return "Int" if (inLanguage == "Swift") else "int "
    elif isinstance(value, list):
        return "[{0}]".format(key) if (inLanguage == "Swift") else "NSArray<{} *> *".format(key)
    elif isinstance(value, dict):
        return key if (inLanguage == "Swift") else "{} *".format(key)
    elif not value:
        return "<#String#>" if (inLanguage == "Swift") else "<#NSString *#>"
    else:
        return "String" if (inLanguage == "Swift") else "NSString *"

# oc 的属性修饰符
def oc_modifier(aType):
    if aType == "NSString *":
        return "copy"
    elif aType == "<#NSString *#>":
        return "copy"
    elif aType == "double ":
        return "assign"
    elif aType == "BOOL ":
        return "assign"
    elif aType == "int ":
        return "assign"
    else:
        return "strong"
  
# 类结束符
def endfix():
    return "}" if (inLanguage == "Swift") else "@end"
  
# 文件后缀
def postfix():
    return "swift" if (inLanguage == "Swift") else "h"

# 类名
def clsName(key):
    first = key.capitalize()[0]
    return "%s%s" % (inPrefix, "{}{}".format(first, key[1:]))

# 生成类名
def classStr(name):
    if inLanguage == "Swift":
        return "%s %s %s%s {" % (inModifier, inType, name, parentCls())
    elif inLanguage == "Objective-C":
        return "@interface {} {}\n".format(name, parentCls())

# 生成属性字符串
def propertyStr(key, value):
    aType = convetType(value, clsName(key))
    if inLanguage == "Swift":
        return '    {0} var {1}: {2}?'.format(inModifier, key, aType)
    elif inLanguage == "Objective-C":
        return "@property(nonatomic, {}){}{};".format(oc_modifier(aType), aType, key)

# 处理字典
def proDict(dic, name = ""):
    if name != "":
        classNames.append(name)
    
    if not isinstance(dic, dict):
        return
    for (key, value) in dic.items():
        if isinstance(value, dict):
            proDict(value, clsName(key))
        elif isinstance(value, list):
            proList(value, clsName(key))

        keyItems.append(Result(key, propertyStr(key, value), name))

# 处理数组
def proList(lis, name = ""):
    pro = lis[0]
    proDict(pro, name)

# 具体显示内容
def display():
    # 添加文件描述
    resContents.append(header())
    
    for cls in classNames:
        resContents.append(classStr(cls))
        for r in keyItems:
            if r.name == cls:
                resContents.append(r.define)
        addStructure(cls)
        
        resContents.append("")
        resContents.append(endfix())
        resContents.append("")
        resContents.append("")
    return resContents

# 分析数据
def analysis(js, name):
    if isinstance(js, dict):
        proDict(js, name)
    elif isinstance(js, list):
        proList(js, name)

# 执行

# 待解析字符串
inInput = sys.argv[1]

# 解析参数
if len(sys.argv) >= 5:
    inParser = sys.argv[2]
    inClcName = sys.argv[3]
    inPrefix = sys.argv[4]
    inType = sys.argv[5]
    inModifier = sys.argv[6]
    inLanguage = sys.argv[7]

try:
    analysis(json.loads(inInput), clsName(inClcName))
    # 输出
    dis = display()
    print(''.join([line+'\n' for line in dis]))
except ValueError, e:
    print(e.message)
