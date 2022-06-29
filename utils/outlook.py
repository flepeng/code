# -*- coding:utf-8 -*-
"""
    @Time  : 2022/2/22  14:39
    @Author: Feng Lepeng
    @File  : outlook.py
    @Desc  :
"""
import base64
import re
from email.mime.image import MIMEImage
from flask import render_template


class OutlookHtml(object):
    def __init__(self, submit_uuid, s_type):
        self.submit_uuid = submit_uuid
        self.s_type = s_type
        self.msgImage_list = []

    def handle_image(self, handle_str, image_num):
        if self.s_type != 'email':
            return handle_str, image_num

        # outlook需要特定的写法，才可以显示图片。<img src="data:image/jpeg;base64,/9j/4AAQSk" style="max-width: 100%;">
        re_ret = re.findall('src="data:image/(.*?);base64,(.*?)"', handle_str)
        for j in re_ret:
            handle_str = handle_str.replace('src="data:image/{};base64,{}"'.format(j[0], j[1]),
                                            'src="cid:image{}" width="600"'.format(image_num))
            msgImage = MIMEImage(base64.b64decode(j[1]))
            msgImage.add_header('Content-ID', 'image{}'.format(image_num))
            self.msgImage_list.append(msgImage)
            image_num += 1
        return handle_str, image_num

    def create_23(self):
        """
        所有的漏洞
        :return:
        """
        image_num = 0

        render_dict = {
            'owner': "",
            'start_data': "",
            'end_data': "",
            'vul_total': 0,
            'vul_import': 0,
            'vul_high': 0,
            'vul_medium': 0,
            'vul_low': 0,
            'vul_total_level': '',
            'vul_list': [],
            'test': "",
        }

        ret = render_template('megvul/email/23.html', render_dict=render_dict)

        return ret, self.msgImage_list


if __name__ == '__main__':
    pass
