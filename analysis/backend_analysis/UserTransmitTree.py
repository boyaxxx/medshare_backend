# -*- coding:utf-8 -*-

class TreeNode:
    viewer_id = None
    share_id = None
    viewer_name = ''
    share_name = ''
    children = []

    def __init__(self, viewer_id, viewer_name, share_id, share_name):
        self.viewer_name = viewer_name
        self.share_name = share_name
        self.viewer_id = viewer_id
        self.share_id = share_id
        self.children = []