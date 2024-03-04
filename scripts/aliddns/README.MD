
# 说明

通过python3 调用 阿里云sdk 实现域名解析

# 使用方法

## 使用前准备工作

### 安装虚拟环境

建议养成使用虚拟环境的习惯

防止多个项目代码使用的库产生冲突

    进入想要放脚本的目录
    如：
    cd /data/scripts/aliddns
    python3 -m venv venv

    把 aliddns.py aliddns.yaml requirements.txt 放到目录里

    安装依赖库
    /data/scripts/aliddns/venv/bin/pip install wheel setuptools
    /data/scripts/aliddns/venv/bin/pip install -r requirements.txt

### 配置文件

    # 配置文件说明 aliddns.yaml

    access_key_id: LTAI5t7exxxxx  # 阿里云获取的密钥id
    access_key_secret: soymxxxxxx # 阿里云获取的密钥key
    domain_records:
      - domain_name: my.domainname
        rr: test-ipv6
        type: AAAA
      - domain_name: my.domainname
        rr: test-ipv4
        type: A

    domain_records 支持配置多项解析
    上述配置模版表示
    添加/更新 test-ipv6.my.domainname 到 ipv6 地址
    添加/更新 test-ipv4.my.domainname 到 ipv4 地址

    可以按照格式 增加 要解析的域名

    提示：如果使用ipv6 需要注意域名不要泄漏 除非你明确配置了防火墙

### 解析逻辑

读取配置文件

获取 ipv4 ipv6 ip地址

调用阿里云sdk 如果存在域名记录则更新 如果不存在记录则新增

## 运行脚本

    保险起见使用绝对路径运行

    /data/scripts/aliddns/venv/bin/python /data/scripts/aliddns/aliddns.py /data/scripts/aliddns/aliddns.yaml


    同时可以添加 crontab 计划任务(如果你对crontab 熟悉的话)
    下面表示每10分钟执行一次脚本

    */10 * * * * /data/scripts/aliddns/venv/bin/python /data/scripts/aliddns/aliddns.py /data/scripts/aliddns/aliddns.yaml >/data/scripts/aliddns/aliddns.log 2>&1
