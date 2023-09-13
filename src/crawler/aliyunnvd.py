#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# @Time   : 2020/4/25 22:17
# @File   : aliyunnvd.py
# -----------------------------------------------
# aliyun：https://avd.aliyun.com/nvd/list
# -----------------------------------------------

from src.bean.cve_info import CVEInfo
from src.crawler._base_crawler import BaseCrawler
from color_log.clog import log
import requests
import json
import re
import time


class Aliyunnvd(BaseCrawler):

    def __init__(self):
        BaseCrawler.__init__(self)
        self.name_ch = '阿里云漏洞库'
        self.name_en = 'nvd ali'
        self.home_page = 'https://avd.aliyun.com/nvd/list'
        self.url_list = 'https://avd.aliyun.com/nvd/list'
        self.url_cve = 'https://avd.aliyun.com/detail?id='


    def NAME_CH(self):
        return self.name_ch


    def NAME_EN(self):
        return self.name_en


    def HOME_PAGE(self):
        return self.home_page


    def get_cves(self, limit = 6):
        params = {
            'length': limit,
            'start' : 0
        }

        response = requests.get(
            self.url_list,
            headers = self.headers(),
            params = params,
            timeout = self.timeout
        )

        cves = []
        if response.status_code == 200:
            json_obj = json.loads(response.text)
            for obj in json_obj.get('data'):
                cve = self.to_cve(obj)
                if cve.is_vaild():
                    cves.append(cve)
                    # log.debug(cve)
        else:
            log.warn('获取 [%s] 威胁情报失败： [HTTP Error %i]' % (self.NAME_CH(), response.status_code))
        return cves


    def to_cve(self, json_obj):
        cve = CVEInfo()
        cve.src = self.NAME_CH()
        cve.url = self.url_cve + (json_obj.get('id') or '')
        cve.info = (json_obj.get('description') or '').strip().replace('\n\n', '\n')

        seconds = json_obj.get('update_time') or json_obj.get('add_time') or 0
        localtime = time.localtime(seconds)
        cve.time = time.strftime('%Y-%m-%d %H:%M:%S', localtime)

        title = json_obj.get('title') or ''
        cve.title =  re.sub(r'CVE-\d+-\d+:', '', title).strip()

        rst = re.findall(r'(CVE-\d+-\d+)', title)
        cve.id = rst[0] if rst else ''
        return cve
