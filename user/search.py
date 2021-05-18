import pdb

from django.http import HttpResponse
from django.shortcuts import render
from utils.utils import search_yummly


class SearchResult:
    def __init__(self):
        self.q = ''
        self.title = ''
        self.author = ''
        self.body = ''

    def get_absolute_url(self):
        return ''


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


# 表单
def search_form(request):
    return render(request, 'search-form.html')


# 接收请求数据
def search(request):
    request.encoding = 'utf-8'
    if 'q' in request.GET and request.GET['q']:
        # message = '你搜索的内容为: ' + request.GET['q']
        query = request.GET['q']
        search_yummly_results = search_yummly(query=query, url_num=5)
        object_list = []
        for result in search_yummly_results:
            object_list.append(Struct(**result))
        return render(request, 'search.html', {'query': query, 'object_list': object_list,})
    else:
        message = '你提交了空表单'
        return HttpResponse(message)
