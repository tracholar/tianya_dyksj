# coding:utf-8

import urllib,urllib2, re, lxml, urlparse, os, md5, time
from lxml import etree
from StringIO import StringIO


# 地缘看世界URL
base_url = 'http://bbs.tianya.cn/post-worldlook-223829-1.shtml'
url_template = 'http://bbs.tianya.cn/post-worldlook-223829-%d.shtml'
def get_page_url(page):
	return (url_template % page)

def get_data_from_url(url):
	
	print '[visit]', url
	headers = {
		'Referer':'http://bbs.tianya.cn/post-worldlook-223829-1.shtml',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36'
	}
	req = urllib2.Request(url, headers = headers)
	try:
		data = urllib2.urlopen(req).read()
	except Exception:
		data = ''
	return 

def get_dom_from_html(html):
	return etree.parse(StringIO(html), etree.HTMLParser())
	
def get_dom_from_url(url):
	html = get_data_from_url(url)
	T = get_dom_from_html(html)
	return T
	
def dom_to_html(T):
	return etree.tostring(T, pretty_print=True, method="html")

def parse_post_div(post_div):
	# print post_div.attrib
	if 'js_username' in post_div.attrib:
		author = urllib.unquote(post_div.attrib['js_username']).decode('utf-8','ignore')
		datetime = post_div.attrib['js_restime']
	else:
		author = '鄙视抢沙发的'.decode('utf-8')
		datetime = '2009-07-12 12:00:00'
	content = post_div.find('.//div[@class="bbs-content"]')
	if content is None:
		content = post_div.find('.//div[@class="bbs-content clearfix"]')
	# print content
	content = dom_to_html(content)
	
	content = preprocess_post(author, datetime, content)
	return author, datetime, content
def save_file_from_url(url, path):
	data = get_data_from_url(url)
	f = open(path, 'wb')
	f.write(data)
	f.close()
	
def get_local_single_post_path(author, datetime):
	fname = datetime[:10] +'-'+ author 
	fname = re.sub(r'[:\\\/\?\*\"\<\>\|\r\n]',' ', fname)
	path = './data/%s.html' % fname.encode('gbk','ignore')
	return path

def preprocess_post(author, datetime, content):
	T = get_dom_from_html(content)
	imgs = T.findall('.//img')
	if imgs is not None:
		for img in imgs:
			img_path = './data/images/'+md5.new(img.attrib['original']).hexdigest()+'.jpg'
			save_file_from_url(img.attrib['original'], './images/'+md5.new(img.attrib['original']).hexdigest()+'.jpg')
			print '[saved]', img.attrib['original']
			
			content = content.replace(img.attrib['src'], img_path)
			
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
		print author, datetime
		if author is '鄙视抢沙发的'.decode('utf-8'):
			post_path = get_local_single_post_path(author, datetime)
			write_to_file(content, post_path)
			print '[saved]', post_path.encode('gbk','ignore')
		fpage.write(content.encode('utf-8') + '\r\n')
	
	fpage.close()
	print '[saved]', page_path
	time.sleep(5)
	
	
def main():
	T = get_dom_from_url(base_url)
	page_num = T.find('//div[@class="atl-pages"]/form/a[last()-1]').text
	page_num = int(page_num)
	for i in range(1,page_num+1):
		save_page(i)
	
	
if __name__ == '__main__':
	main()

	