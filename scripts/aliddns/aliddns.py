
# -*- coding: utf-8 -*-

import os
import sys

from loguru import logger
import requests

from ruamel.yaml import YAML
import traceback

from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CredConfig
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models


class AlicloudApi:
    
    def __init__(self, access_key_id: str='', access_key_secret: str=''):
        config = CredConfig(
            type='access_key',
            access_key_id=access_key_id,
            access_key_secret=access_key_secret

        )
        self.cred = CredClient(config)
        self.domains = []
        self.domain_records = {}
        endpoint = 'alidns.cn-hangzhou.aliyuncs.com'
        config = self.__make_config(endpoint)
        self.client = Alidns20150109Client(config)

        self.describe_domains()

    def __make_config(self, endpoint: str):
        try:
            config = open_api_models.Config(
                credential=self.cred,
                endpoint=endpoint,
                connect_timeout=3000
            )
            return config
        except Exception as e:
            tb = traceback.format_exc()
            logger.error('get config error %s\n traceback: %s' % (e, tb))
    
    def describe_domains(self):
        describe_domains_request = alidns_20150109_models.DescribeDomainsRequest()
        runtime = util_models.RuntimeOptions()

        try:
            # 复制代码运行请自行打印 API 的返回值
            response = self.client.describe_domains_with_options(
                describe_domains_request, runtime).body

            for domain in response.domains.domain:
                self.domains.append(domain.domain_name)

            if not self.domains:
                logger.error('获取域名列表失败!请检查密钥权限设置是否正确!')
                exit(100)

        except Exception as error:
            # 错误 message
            logger.error(error)
            exit(100)
        
    def describe_domain_records(self, domain_name):

        describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
            domain_name=domain_name
        )
        runtime = util_models.RuntimeOptions()

        try:
            response = self.client.describe_domain_records_with_options(
                describe_domain_records_request, runtime).body

            for dr in response.domain_records.record:
                self.domain_records.update(
                    {'%s.%s' % (dr.rr, domain_name): '%s|%s' % (dr.record_id, dr.value)}
                )

        except Exception as error:
            # 错误 message
            logger.error(error)
            exit(100)

    def add_domain_record(self, domain_name, rr, rtype, value):
        add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
            domain_name=domain_name,
            rr=rr,
            type=rtype,
            value=value
        )
        runtime = util_models.RuntimeOptions()

        try:
            # 复制代码运行请自行打印 API 的返回值
            self.client.add_domain_record_with_options(add_domain_record_request, runtime).body
            logger.info('域名解析添加成功! %s.%s -> %s, type: %s' % (rr, domain_name, value, rtype))

        except Exception as error:
            # 错误 message
            logger.error(error)
            exit(100)

    def update_domain_record(self, record_id, rr, rtype, value, domain_name):
        endpoint = 'alidns.cn-hangzhou.aliyuncs.com'
        config = self.__make_config(endpoint)
        client = Alidns20150109Client(config)

        update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
            record_id=record_id,
            rr=rr,
            type=rtype,
            value=value
        )
        runtime = util_models.RuntimeOptions()

        try:
            # 复制代码运行请自行打印 API 的返回值
            client.update_domain_record_with_options(update_domain_record_request, runtime).body
            logger.info('域名解析更新成功! %s.%s -> %s, type: %s' % (rr, domain_name, value, rtype))

        except Exception as error:
            # 错误 message
            logger.error(error)
            exit(100)

    def validate_record(self, record_config):
            need_config_key = ['domain_name', 'rr', 'type']

            for k in need_config_key:
                if k not in record_config or record_config.get(k, None) is None:
                    logger.error('record 配置必须包含 %s 字段!')
                    exit(100)
            
            if record_config.get('domain_name', '') not in self.domains:
                logger.error('当前账号不存在域名: %s!' % record_config.get('domain_name', ''))
                exit(100)

    def record_op(self, ipv4: str, ipv6:str, records: list):
        for record_config in records:
            self.validate_record(record_config)
            domain_name = record_config.get('domain_name', None)
            rr = record_config.get('rr', None)
            rtype = record_config.get('type', None)

            if rtype == 'AAAA':
                if ipv6 is None:
                    logger.error('当前主机不支持ipv6, 此记录跳过 %s' % rr)
                    continue
                value = ipv6
            if rtype == 'A':
                value = ipv4

            self.describe_domain_records(domain_name)

            full_domain = '%s.%s' %(rr, domain_name)

            old_record =  self.domain_records.get(full_domain, None)

            if old_record:
                record_id, old_value = old_record.split('|')
                if old_value == value:
                    # ip地址 没有变化
                    continue
                self.update_domain_record(
                    record_id, rr, rtype, value, domain_name
                )
            else:
                self.add_domain_record(
                    domain_name, rr, rtype, value
                )

def check_args(args: list):
    if len(args) != 2:
        return False
    if os.path.exists(args[1]):
        return args[1]
    else:
        return False

def load_config(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as cf:
            yaml = YAML(typ='rt')
            return yaml.load(cf.read())
    except Exception as e:
        logger.error('read config file [%s] error: %s' % (config_file, e))
        return {}

def get_ip_address():
    try:
        resp = requests.get('http://4.ipw.cn')
        ipv4 = resp.text
    except Exception as e:
        ipv4 = None

    try:
        resp = requests.get('http://6.ipw.cn')
        ipv6 = resp.text
    except Exception as e:
        logger.error('当前主机不支持ipv6!')
        ipv6 = None

    return ipv4, ipv6


def main():
    args = sys.argv
    config_file = check_args(args)
    if not config_file:
        logger.error('配置文件不存在! 阅读README 查看使用方法')
        exit(100)
    else:
        config = load_config(config_file)
        access_key_id = config.get('access_key_id', None)
        access_key_secret = config.get('access_key_secret', None)
        domain_records = config.get('domain_records', None)

        if domain_records is None:
            logger.error('配置文件内容不正确!必须配置 domain_records 阅读README 查看使用方法')
            exit(100)
        if access_key_secret is None:
            logger.error('配置文件内容不正确!必须配置 access_key_secret 阅读README 查看使用方法')
            exit(100)
        if access_key_id is None:
            logger.error('配置文件内容不正确!必须配置 access_key_id 阅读README 查看使用方法')
            exit(100)

        if not domain_records:
            logger.error('配置文件没有配置任何待解析内容! 阅读README 查看使用方法')
            exit(100)

        ipv4, ipv6 = get_ip_address()

        alicloud_client = AlicloudApi(access_key_id, access_key_secret)
        alicloud_client.record_op(ipv4, ipv6, domain_records)


if __name__ == '__main__':
    main()