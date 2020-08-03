
from email.mime.text import MIMEText
import smtplib, ssl
from smtplib import SMTP   
from email.mime.multipart import MIMEMultipart # sending email
from email.mime.text import MIMEText  # constructing messages
from jinja2 import Environment        # Jinja2 templating\

import numpy as np
import afinn
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pyhive import hive
import datetime

stock_lists = {'aapl':'APPLE, Inc.',
               'msft':'Microsoft Corporation',
               'amzn':'Amazon.com, Inc.',
               'baba':'Alibaba Group Holding Limited',
               'fb':'Facebook, Inc.'
               ,
               'googl':'Alphabet Inc.',
               'jnj':'Johnson & Johnson',
               'wmt':'Walmart Inc. ',
               'v':'Visa Inc.',
               'ma':'Mastercard Incorporated'
              }
selectedcol = ['pubdate','title','url','summary','score','host']+list(stock_lists.keys())


newscard=''
stockcard=''
for stk in stock_lists:
    ss = f'select pubdate, title, url, summary,score, host from nutch_ext where {stk} is NOT NULL '
    
    conn = hive.Connection(host ='daou-bd-r01a01', port = 10000)
    cursor = conn.cursor()
    cursor.execute(ss)
    news_coll = cursor.fetchall()
    news_list = [{selectedcol[i] : a[i] for i in range(len(a))} for a in news_coll ]
    news_list = [{ k: datetime.datetime.strptime(v, "%Y%m%d%H%M%S") if k == 'pubdate' else v for k,v in x.items()} for x in news_list]
    news_list =  [dict(item, **{'name':stock_lists[stk]}) for item in news_list]
    news_list = sorted(news_list, key=lambda k: k['pubdate']) 
    
    
    #calcualte score
    scoresss = [float(a['score']) for a in news_list]
    q1 = np.percentile(scoresss,25)
    q3 = np.percentile(scoresss,75)
    
    #give polarity 
    for a in news_list:
        if float(a['score']) < q1:
            a['polarity'] = 'negative'
        elif float(a['score']) > q3:
            a['polarity'] ='positive'
        else:
            a['polarity'] = "neutral"
    
        
    recent10= sorted(news_list, key=lambda d: d['pubdate'], reverse=True)[:10]
    for r in recent10:
        r['pubdate'] = r['pubdate'].strftime('%B %d %Y')
        
        
    nownow = datetime.datetime.today().strftime('%B %d %Y')
    newsboxhtml = ''
    for a in recent10:
        STK = stk.upper()
        url = a['url']
        title = a['title']
        summary = a['summary']
        host = a['host']
        pubdate = a['pubdate']
        name = a['name']
        polarity= a['polarity']
        if polarity =='negative':
            color='#c62f2d'
        elif polarity=='positive':
            color='#25780e'
        else:
            color='#f1ebec'
            
            
        newscardtp = f"""<div class="card">
                    <div style="color:#4a2217;" class="titlesearch"><a href=\"{url}\">{title}</a></div>
                    <div class="textsearch">{summary}</div>
                    <div style="float:left;"><span class="bottomticker">{STK}</span><span class="bottomsearchtext"> {host} | {pubdate} </span></div>
                    <div style="text-align:right;"><span style="font-size:0.9rem;color:{color}; line-height:1rem ">{polarity}</span></div>
                <div style="border-top: 0.9rem solid transparent;"></div></div>"""
        
        newscard += newscardtp
        
       
    stockcardtp =f"""  <div style="color:#400e0d; font-family:Helvetica;font-size:16px;background-color:#eddfe1;display: inline-block;">{name}</div>
                          <div align="center"><img src="https://github.com/Irenejy93/daouHTMLimg/blob/master/polarity_{STK}.png?raw=true " width="500px" height="150px"></div>

                            <div class="cardbox">
                                <div class="card-items">

                                                        {newscard}

                                                    </div>
                            </div>

                            <div><br><hr style="width=80%;size=1px;opacity:0.2; background-color:#D3D3D3;border: 0 ;"/></div>"""
    newscard=''
    stockcard +=stockcardtp

    
 
newsectionhtml=f"""<div style="text-align: center; inline-block">{stockcard}
                            </div>"""

TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://stocknewsapi.com/css/stylelanding.css?v=2.3" rel="stylesheet">
    <link href="https://stocknewsapi.com/css/prims.css" rel="stylesheet">
    <title>FromScratch</title>

    <title>Title</title>
</head>
<body style="background:#F6F8FA; margin:0 auto;">
<!--class container-->
<div style="background:#fff; max-width:80%; margin:auto;">
<!--    site-->
    <div style="border-top: 0.2rem solid transparent;
        border-image: linear-gradient(to right, #c62f2d 0%, #c62f2d 100%);
        border-image-slice: 1;
        z-index: 999;"></div>

    <header style="margin-top:10px; margin-bottom:20px; position:relative; padding:15px 0 15px; ">
        <div class="container">
            <div class="site-header-inner">
                <div class="brand header-brand">
                    <h1 class="m-0">
                        <div style="border-top: 0.2rem solid transparent;
        border-image: linear-gradient(to right, #fff 0%, #fff 100%);
        border-image-slice: 1;
        z-index: 999;"></div>
                        <img src="http://www.kiwoomam.com/assets/images/common/logo.jpg " width="150px" height="70px"
                            alt="Stocknewsapi Logo">
                    </h1>
                </div>
                <div class="margin-right: 0">
                </div>
            </div>
        </div>
        <div><br></div>
    </header>
<!--    main start-->
    <main>
        <div id="demo" class="hero text-center">
            <div style="width: 100%;
        margin: 0 auto;
        padding-left: 16px;
        padding-right: 16px;">
                <h1 style=" color:#300201;font-family:Bahnschrift Condensed;font-size:2.3rem;" class="hero-title h2-mobile mt-0 is-revealing">DAOU DAILY STOCK</h1>

                <div align="center"><img src="https://github.com/Irenejy93/daouHTMLimg/blob/master/dailynewscount.png?raw=true" width="550px" height="30px">
</div><br>

                <div style="color:#4f2b2b;opacity:0.8;" class="hero-paragraph is-revealing">
                    Latest news for the large capital companies from the reliable news sources. News are given with
                    their keywords, summary and polarity
                </div>
                <div><br><br></div>
            </div>
        </div>
            <div>
                <div style="width: 100%;
        margin: 0 auto;
        padding-left: 50px;
        padding-right: 50px;">

                    {newsectionhtml}

            </div>
            </div>
    </main>
<!-- footer start-->
    <footer class="site-footer text-light">
        <div class="container">
            <div class="site-footer-inner">
                <div class="brand footer-brand" style="margin-top: 0px">
                    &nbsp;
                </div>
                <ul class="footer-links list-reset">
                    <li>
                        <a style="color:#C6C6C6;" href="/contact">irenee.jy93@gmail.com</a>
                    </li>
                </ul>
                <ul class="footer-social-links list-reset">

                </ul>
                <div style="color:#C6C6C6;" class="footer-copyright">Updated on July 29 2020 </div>
            </div>
        </div>
    </footer>
    <!-- footer end-->


</div>

</body>
</html>"""

TEMPLATE = TEMPLATE.replace('\n','')






msg = MIMEText(
    Environment().from_string(TEMPLATE).render(
        title='Hello World!'
    ), "html"
)

subject = "newsletter with graph"
sender= "irenee.jy93@daou.co.kr"
recipient ="irenee.jy93@daou.co.kr"

msg['Subject'] = subject
msg['From'] = sender
msg['To'] = dhk

# Send the message via our own local SMTP server.
s = SMTP('localhost')
s.sendmail(sender, [recipient], msg.as_string())
s.quit()
