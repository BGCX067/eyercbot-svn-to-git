# HTML to IRC
# Converts html found in google and wikipedia into irc compatable format

import re

# Strip out html tags
def html2irc(html):
	html = html.replace('&middot;', '*')
	html = html.replace('<b>','')
	html = html.replace('</b>','')
	html = html.replace('<em>','')
	html = html.replace('</em>','')
	html = re.sub('<a.*?>', '', html)
	html = re.sub('<sup.*?</sup>', '',  html)
	html = html.replace('</a>','')
	html = html.replace('&#39;', "'")
	html = html.replace('<i>',  '')
	html = html.replace('</i>', '' )
	html = html.replace('\x02', '')
	html = html.replace('&amp;', '&')
	html = html.encode('utf8').replace('\xb2',  '')
	return html.encode('ascii')
	
	
	'''      
shamelessly taken from the  rssnews.tcl for eggdrop

&quot;     \x22  &apos;     \x27  &amp;      \x26  &lt;       \x3C
        &gt;       \x3E  &nbsp;     \x20  &iexcl;    \xA1  &curren;   \xA4
        &cent;     \xA2  &pound;    \xA3  &yen;      \xA5  &brvbar;   \xA6
        &sect;     \xA7  &uml;      \xA8  &copy;     \xA9  &ordf;     \xAA
        &laquo;    \xAB  &not;      \xAC  &shy;      \xAD  &reg;      \xAE
        &macr;     \xAF  &deg;      \xB0  &plusmn;   \xB1  &sup2;     \xB2
        &sup3;     \xB3  &acute;    \xB4  &micro;    \xB5  &para;     \xB6
        &middot;   \xB7  &cedil;    \xB8  &sup1;     \xB9  &ordm;     \xBA
        &raquo;    \xBB  &frac14;   \xBC  &frac12;   \xBD  &frac34;   \xBE
        &iquest;   \xBF  &times;    \xD7  &divide;   \xF7  &Agrave;   \xC0
        &Aacute;   \xC1  &Acirc;    \xC2  &Atilde;   \xC3  &Auml;     \xC4
        &Aring;    \xC5  &AElig;    \xC6  &Ccedil;   \xC7  &Egrave;   \xC8
        &Eacute;   \xC9  &Ecirc;    \xCA  &Euml;     \xCB  &Igrave;   \xCC
        &Iacute;   \xCD  &Icirc;    \xCE  &Iuml;     \xCF  &ETH;      \xD0
        &Ntilde;   \xD1  &Ograve;   \xD2  &Oacute;   \xD3  &Ocirc;    \xD4
        &Otilde;   \xD5  &Ouml;     \xD6  &Oslash;   \xD8  &Ugrave;   \xD9
        &Uacute;   \xDA  &Ucirc;    \xDB  &Uuml;     \xDC  &Yacute;   \xDD
        &THORN;    \xDE  &szlig;    \xDF  &agrave;   \xE0  &aacute;   \xE1
        &acirc;    \xE2  &atilde;   \xE3  &auml;     \xE4  &aring;    \xE5
        &aelig;    \xE6  &ccedil;   \xE7  &egrave;   \xE8  &eacute;   \xE9
        &ecirc;    \xEA  &euml;     \xEB  &igrave;   \xEC  &iacute;   \xED
        &icirc;    \xEE  &iuml;     \xEF  &eth;      \xF0  &ntilde;   \xF1
        &ograve;   \xF2  &oacute;   \xF3  &ocirc;    \xF4  &otilde;   \xF5
        &ouml;     \xF6  &oslash;   \xF8  &ugrave;   \xF9  &uacute;   \xFA
        &ucirc;    \xFB  &uuml;     \xFC  &yacute;   \xFD  &thorn;    \xFE
        &yuml;     \xFF
'''
