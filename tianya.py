# coding:utf-8

import urllib,urllib2, re, lxml, urlparse, os, md5, time
from lxml import etree
from StringIO import StringIO
from HTMLParser import HTMLParser
import thread, threading, sys

# 地缘看世界URL
base_url = 'http://bbs.tianya.cn/post-worldlook-223829-1.shtml'
url_template = 'http://bbs.tianya.cn/post-worldlook-223829-%d.shtml'

html_parser = HTMLParser()
pages = []
pages_lock = thread.allocate_lock()


def html_parse(html):
	return html_parser.unescape(html)
	
def get_page_url(page):
	return (url_template % page)

def get_data_from_url(url):
	
	print '[visit]', url
	headers = {
		'Referer':'http://bbs.tianya.cn/post-worldlook-223829-1.shtml',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36',
		'Cookie':'__guid2=2108452181; __utma=22245310.1924145466.1351944891.1408253603.1410408002.23; __utmz=22245310.1410408002.23.21.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); time=ct=1422815005.798; __u_a=v2.3.0; Hm_lvt_bc5755e0609123f78d0e816bf7dee255=1422808285,1422808481,1422808494; Hm_lpvt_bc5755e0609123f78d0e816bf7dee255=1422815007'
	}
	req = urllib2.Request(url, headers = headers)
	try:
		data = urllib2.urlopen(req).read()
	except Exception:
		data = ''
	return data

def get_dom_from_html(html):
	return etree.parse(StringIO(html), etree.HTMLParser())
	
def get_dom_from_url(url):
	html = get_data_from_url(url)
	T = get_dom_from_html(html)
	return T
	
def dom_to_html(T):
	return etree.tostring(T, pretty_print=True)

def parse_post_div(post_div):
	# print post_div.attrib
	if 'js_username' in post_div.attrib:
		author = urllib.unquote(post_div.attrib['js_username']).decode('utf-8','ignore')
		datetime = post_div.attrib['js_restime']
	else:
		author = '鄙视抢沙发的'.decode('utf-8')
		datetime = '2009-07-12 12:00:00'
	author = html_parse(author)
	content = post_div.find('.//div[@class="bbs-content"]')
	if content is None:
		content = post_div.find('.//div[@class="bbs-content clearfix"]')
	# print content
	content = dom_to_html(content)
	
	content = html_parse(preprocess_post(author, datetime, content))
	return author, datetime, content
def save_file_from_url(url, path):
	if os.path.exists(path):
		return
	data = get_data_from_url(url)
	f = open(path, 'wb')
	f.write(data)
	f.close()
	
def get_local_single_post_path(author, datetime):
	fname = re.sub(r'[\s\:]','-',datetime) +'-'+ author 
	fname = re.sub(r'[:\\\/\?\*\"\<\>\|\r\n]',' ', fname)
	path = './data/%s.html' % fname.encode('gbk','ignore')
	return path

def preprocess_post(author, datetime, content):
	T = get_dom_from_html(content)
	imgs = T.findall('.//img')
	if imgs is not None:
		for img in imgs:
			img_name = md5.new(img.attrib['original'].encode('utf-8','ignore')).hexdigest()+'.jpg'
			img_path = './data/images/'+img_name
			
			save_file_from_url(img.attrib['original'], img_path)
			print '[saved]', img.attrib['original'], img_path
			
			content = content.replace(img.attrib['src'], './images/'+img_name)
			
	content = '<p>%s %s</p><div>%s</div>' % (author, datetime, content)
	return content
	
def write_to_file(content, path):
	if os.path.exists(path):
		return
	f = open(path, 'wb')
	f.write(content)
	f.close()
		
def save_page(page):
	url = get_page_url(page)
	
	T = get_dom_from_url(url)
	post_divs = T.findall('//div[@class="atl-item"]')
	page_path = './data/page-%d.html' % page
	
	fpage = open(page_path, 'wb')
	for div in post_divs:
		author, datetime, content = parse_post_div(div)
		# print author, datetime
		# print repr('鄙视抢沙发的'.decode('utf-8'))
		# print repr(html_parse(author))
		if author == '鄙视抢沙发的'.decode('utf-8'):
			post_path = get_local_single_post_path(author, datetime)
			if os.path.exists(post_path):
				continue
			write_to_file(content.encode('utf-8','ignore'), post_path)
			print '[saved]', post_path
		fpage.write(content.encode('utf-8','ignore') + '\r\n')
	
	fpage.close()
	print '[saved]', page_path
	time.sleep(5)
	
def get_visisted_urls():
	return open('urls.txt','r').read().split('\n')
def save_visited_url(url):
	f = open('urls.txt','a')
	f.write(url + '\n')
	f.close()

def crawl():
	pages_lock.acquire()
	if len(pages)==0:
		pages_lock.release()
		print '[exit]', 'threading exit!'
		return
	i = pages.pop(0)
	pages_lock.release()
	
	url = get_page_url(i)
	if url not in visited_urls:		
		save_page(i)
		save_visited_url(url)
	crawl()
	

	
if __name__ == '__main__':
	T = get_dom_from_url(base_url)
	page_num = T.find('//div[@class="atl-pages"]/form/a[last()-1]').text
	page_num = int(page_num)
	visited_urls = get_visisted_urls()
	pages = range(1,page_num+1)
	
	
	for i in range(20):
		threading.Thread(target=crawl).start()
	

	