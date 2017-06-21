#! /usr/bin/python3
import sys
import html
sys.path.append('..')
from pygiftparser import parser as pygift
import yattag

import glob


d = yattag.Doc() 
d.asis('<!DOCTYPE html>')
with d.tag('html'):
    with d.tag('head'):
        d.stag('meta', charset="utf-8")
        d.stag('link', rel="stylesheet", href="default.css", type="text/css")
        d.stag('link', rel="stylesheet", href="libs/tocible-master/jquery.tocible.css", type="text/css")
        with d.tag('body'):
            d.asis("""
            <script src="http://code.jquery.com/jquery-1.12.0.min.js"></script>
            <script src="libs/tocible-master/jquery.tocible.js"></script>
            """)
            with d.tag('div',id='container'):
                with d.tag('div', id='ref'):
                    d.text('')
                with d.tag('div',klass='gifts'):
                    for filename in glob.glob('*gift'):
                        with d.tag('h1'):
                            d.text(filename)
                            
                        with open(filename,'r') as f:
                            questions = pygift.parseFile(f)
                        f.close()
                                
                        for q in questions:
                            with d.tag('div', klass='qandcode'):
                                q.toHTML(d,True)

                                with d.tag('div', klass='full'):
                                    with d.tag('pre'):
                                        d.asis(html.escape(q.full))

            d.asis("""
            <script language="javascript">
            $('#container').tocible({
            heading: 'h1', //[selector], the first level heading
            reference:'#ref', //[selector], reference element for horizontal positioning
            title: 'Contents', //[selector or string], title of the menu
            hash: false, //[boolean], setting true will enable URL hashing on click
            offsetTop: 50, //[number], spacing/margin above the menu
            speed: 800, //[number or string ('slow' & 'fast')], duration of the animation when jumping to the clicked content
            collapsible: true, //[boolean], enabling true will auto collapse sub level heading not being scrolled into
            maxWidth: 150 //[number] set max-width of the navigation menu
            });
            </script>
            """)
out =  open("index.html", "w")
out.write (d.getvalue())
out.close()

    
