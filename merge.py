#coding:utf-8
import os, re 
import datetime

ls = os.listdir('./data')
fs = [f for f in ls if re.match(r'\d{4}-(\d{2}-){5}.+', f)]
# fs.sort()

year_month = list(set([f[:7] for f in fs]))
year_month.sort()

header = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    </head>
    <body>
'''
chapter = '<h1>%s</h1>'
footer = '''
    </body>
</html>
'''

for ym in year_month:
    flist = filter(lambda f: f[:7]==ym, fs)
    flist.sort()
    
    
    fo = open(u'data/%s-鄙视抢沙发的.html' % ym, 'w')
    fo.write(header)
    fo.write(chapter % ym)
    for f in flist:
        
        fo.write(open('data/%s' % f).read())
        
    fo.write(footer)
    fo.close()
    
    print '%s-鄙视抢沙发的.html' % ym,