#!/usr/bin/env python2.7

# This script simply produces a working pac file,
# no fancy input arguments support yet.
# If someone is really interested in using this script,
# download the gfwlist.txt, decode it through base64, name it as "gfwlist_decoded.txt"
# and put it in the same direcotry with this script
# run the script in terminal.

import re
import urlparse
import argparse
from collections import defaultdict
import json
import string
import sys
import os
import urllib2
import base64
from itertools import chain
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO


# adjust the address

GFWLIST_URL = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'

#{{{ shExpMatch
SHEXPMATCH = '''
function shExpMatch(url, pat) {

  var pcharcode0;
  var ucharcode0;
  var pcharcode1;

  if (pat.length === 0) {
    if (url.length === 0) {
      return true;
    } else {
      return false;
    }
  }

  if (pat.length === url.length &&
      pat.indexOf('*') < 0 &&
      pat.indexOf('?') < 0) {
    return pat === url;
  }

  ucharcode0 = url.charCodeAt(0);
  pcharcode0 = pat.charCodeAt(0);

  if (pcharcode0 === 42) { // pat[0] === '*'
    pcharcode1 = pat.charCodeAt(1);
    if (isNaN(pcharcode1)) {
      return true;
    } else if (pcharcode1 === 42) { // pat[1] === '*' skip continuous '*'
      return shExpMatch(url, pat.substr(1));
    } else {
      if (url.length === 0) {
        return false;
      }
      if (pcharcode1 === ucharcode0 || pcharcode1 === 63) {
        if (shExpMatch(url.substr(1), pat)) {
          return true;
        } else {
          return shExpMatch(url.substr(1), pat.substr(2));
        }
      } else {
        return shExpMatch(url.substr(1), pat);
      }
    }
  } else if (pcharcode0 === 63) {
    if (url.length === 0) {
      return false;
    }
    return shExpMatch(url.substr(1),pat.substr(1));
  } else {
    if (url.length === 0) {
      return false;
    }
    if (ucharcode0 === pcharcode0) {
      return shExpMatch(url.substr(1),pat.substr(1));
    } else {
      return false;
    }
  }
  return false;
}
'''
#}}}

# top-level domains #{{{
SUFFIX_LIST = (
'.ac','.ad','.ae','.aero','.af','.ag','.ai','.al',
'.am','.an','.ao','.aq','.ar','.arpa','.as','.asia',
'.at','.au','.aw','.ax','.az','.ba','.bb','.be',
'.bf','.bg','.bh','.bi','.biz','.bj','.bm','.bo',
'.br','.bs','.bt','.bv','.bw','.by','.bz','.ca',
'.cat','.cc','.cd','.cf','.cg','.ch','.ci','.cl',
'.cm','.cn','.co','.com','.coop','.cr','.cu','.cv',
'.cw','.cx','.cz','.de','.dj','.dk','.dm','.do',
'.dz','.ec','.edu','.ee','.eg','.es','.eu','.fi',
'.fm','.fo','.fr','.ga','.gb','.gd','.ge','.gf',
'.gg','.gh','.gi','.gl','.gm','.gn','.gov','.gp',
'.gq','.gr','.gs','.gt','.gw','.gy','.hk','.hm',
'.hn','.hr','.ht','.hu','.id','.ie','.im','.in',
'.info','.int','.io','.iq','.ir','.is','.it','.je',
'.jo','.jobs','.jp','.kg','.ki','.km','.kn','.kp',
'.kr','.ky','.kz','.la','.lb','.lc','.li','.lk',
'.lr','.ls','.lt','.lu','.lv','.ly','.ma','.mc',
'.md','.me','.mg','.mh','.mil','.mk','.ml','.mn',
'.mo','.mobi','.mp','.mq','.mr','.ms','.mt','.mu',
'.museum','.mv','.mw','.mx','.my','.na','.name','.nc',
'.ne','.net','.nf','.ng','.nl','.no','.nr','.nu',
'.om','.org','.pa','.pe','.pf','.ph','.pk','.pl',
'.pm','.pn','.post','.pr','.pro','.ps','.pt','.pw',
'.py','.qa','.re','.ro','.rs','.ru','.rw','.sa',
'.sb','.sc','.sd','.se','.sg','.sh','.si','.sj',
'.sk','.sl','.sm','.sn','.so','.sr','.st','.su',
'.sv','.sx','.sy','.sz','.tc','.td','.tel','.tf',
'.tg','.th','.tj','.tk','.tl','.tm','.tn','.to',
'.tp','.travel','.tt','.tv','.tw','.tz','.ua','.ug',
'.us','.uy','.uz','.va','.vc','.ve','.vg','.vi',
'.vn','.vu','.wf','.ws','.yt','.xxx','.bzh','.rio',
'.camera','.clothing','.lighting','.singles','.ventures','.voyage',
'.guru','.holdings','.equipment','.bike','.estate','.tattoo',
'.land','.plumbing','.contractors','.sexy','.menu','.uno',
'.gallery','.technology','.reviews','.guide','.graphics','.construction',
'.onl','.diamonds','.kiwi','.enterprises','.today','.futbol',
'.photography','.tips','.directory','.kitchen','.kim','.monash',
'.wed','.pink','.ruhr','.buzz','.careers','.shoes',
'.career','.otsuka','.gift','.recipes','.coffee','.luxury',
'.domains','.photos','.limo','.viajes','.wang','.democrat',
'.mango','.cab','.support','.dance','.nagoya','.computer',
'.wien','.berlin','.codes','.email','.repair','.holiday',
'.center','.systems','.wiki','.ceo','.international','.solar',
'.company','.education','.training','.academy','.marketing','.florist',
'.solutions','.build','.institute','.builders','.red','.blue',
'.ninja','.business','.gal','.social','.house','.camp',
'.immobilien','.moda','.glass','.management','.kaufen','.farm',
'.club','.voting','.tokyo','.moe','.guitars','.bargains',
'.desi','.cool','.boutique','.pics','.cheap','.photo',
'.network','.zone','.link','.qpon','.agency','.tienda',
'.works','.london','.watch','.rocks','.shiksha','.budapest',
'.nrw','.vote','.fishing','.expert','.horse','.christmas',
'.cooking','.casa','.rich','.voto','.tools','.praxi',
'.events','.flights','.report','.partners','.neustar','.rentals',
'.catering','.community','.maison','.parts','.cleaning','.okinawa',
'.foundation','.properties','.vacations','.productions','.industries','.haus',
'.vision','.mormon','.cards','.ink','.villas','.consulting',
'.cruises','.krd','.xyz','.dating','.exposed','.condos',
'.eus','.caravan','.actor','.saarland','.yokohama','.pub',
'.ren','.fish','.bar','.dnp','.bid','.supply',
'.miami','.supplies','.quebec','.moscow','.globo','.axa',
'.vodka','.rest','.frogans','.wtc','.rodeo','.sohu',
'.best','.country','.kred','.feedback','.work','.luxe',
'.ryukyu','.autos','.homes','.jetzt','.yachts','.motorcycles',
'.mini','.ggee','.beer','.college','.ovh','.meet',
'.gop','.blackfriday','.lacaixa','.vegas','.black','.soy',
'.trade','.gent','.ing','.dad','.shriram','.bayern',
'.scot','.webcam','.foo','.eat','.nyc','.prod',
'.how','.day','.meme','.mov','.paris','.boo',
'.new','.ifm','.life','.archi','.spiegel','.brussels',
'.church','.here','.dabur','.vlaanderen','.cologne','.wme',
'.nhk','.suzuki','.whoswho','.scb','.hamburg','.services')
#}}}

# match list #{{{
PAC_VAR = '''
var PROXY = '${proxy}';
var DLIST = ${domains};
var SEARCH = ${search};
var WHITELIST_TLD = ['cn', 'lan', 'local', 'xn--fiqs8s'];'''
#}}}

# functions ${{{
PAC_FUNC = '''
function FindProxyForURL(url, host) {

	host = host.toLowerCase();

	if (/^\d+\.\d+\.\d+\.\d+$/g.test(host)||
		host === 'localhost') {
		return "DIRECT";
	}

	var xs = host.split('.');

	if (xs.length === 1) {
		return 'DIRECT';
	}

	var suffix = xs[xs.length-1];

	if (WHITELIST_TLD.indexOf(suffix) != -1) {
		return "DIRECT";
	}

	if (suffix in DLIST) {

		var largeTLD = ['com', 'org', 'net'];

		if (largeTLD.indexOf(suffix) != -1) {

			var ssuffix = xs[xs.length-2];

			if (ssuffix.length === 0) {
				return 'DIRECT';
			}

			ssuffix = ssuffix[ssuffix.length-1];

			if (ssuffix in DLIST[suffix]) {
				for (var i = 0; i< DLIST[suffix][ssuffix].length;++i) {
					if (shExpMatch(host,DLIST[suffix][ssuffix][i])){
						return PROXY;
					}
				}
			}

		} else {

			for (var i = 0; i < DLIST[suffix].length;++i) {
				if (shExpMatch(host,DLIST[suffix][i])) {
					return PROXY;
				}
			}
		}
	}

	for (var i = 0; i < DLIST['unknown'].length; ++i) {
		if(shExpMatch(host, DLIST['unknown'][i])) {
			return PROXY;
		}
	}

	for (var i=0;i<SEARCH.length;++i) {
		if (shExpMatch(url, SEARCH[i])) {
			return PROXY;
		}
	}

	return 'DIRECT';
}
'''
#}}}

suffixPtn = re.compile('(\\{0})$'.format('|\\'.join(SUFFIX_LIST)), flags=re.I)

def parse_gfwlist_content(fobj):

	domains = set()
	searches = set()

	httpPtn = re.compile(r'^\|https?://')
	domainPtn = re.compile(r'^\|\|')
	ignorePtn = re.compile(r'^([[@!]|$)')
	slashPtn = re.compile(r'\\\/')
	restPtn = re.compile('^[.\w]')
	letterStartPtn = re.compile(r'^[a-z.]', flags=re.I)
	#suffixPtn = re.compile('(\\{0})$'.format('|\\'.join(SUFFIX_LIST)), flags=re.I)
	#print '(\\{0})$'.format('|\\'.join(SUFFIX_LIST))
	wcMatPtn = re.compile(r'^(.+)(\*[^*]+)+$')
	endwithdot = {True:'*', False:''}
	
	for line in fobj:

		domain = ''

		line = line.strip()

		if ignorePtn.match(line):
			continue

		if line.startswith('/') and line.endswith('/'):
			# regex is too complicated to parse, and there are only a couple of addresses actually wrote in regex,
			# I'd rather write their corresponding wildcard pattern manually.
			continue

		if line.endswith('/'):
			line = line.rstrip('/')

		if line.startswith('search*'):
			searches.add('*/'+line)

		elif letterStartPtn.match(line):

			if suffixPtn.search(line):
				domain = line
			else:

				if '/' in line:
					line = line.split('/')[0]

				mat = wcMatPtn.match(line)

				if mat:
					while True:
						domain = mat.group(1)
						if suffixPtn.search(domain):
							break
						mat = wcMatPtn.match(domain)
						if not mat:
							break
			if domain:
				if line.startswith('.'):
					domains.add(domain.lstrip('.'))
					domains.add('*'+domain)
				else:
					domains.add(domain)
					domains.add('*.'+domain)

		elif httpPtn.match(line):

			pr = urlparse.urlparse(line.lstrip('|'))

			if pr.netloc:
				domains.add(pr.netloc)

		elif domainPtn.match(line):
			_d = line.lstrip('|')
			domains.add('*.'+_d)
			domains.add(_d)

	domains.add('*.google.*')
	domains.add('*.blogspot.*')
	domains.add('*facebook.com')

	discards = set()
	for d in domains:
		if d.startswith('*.www.') or d.endswith('.'):
			discards.add(d)
	domains.difference_update(discards)

	return (domains, searches)

def main(inputs, output, proxy, fetchgfwlist=True, hasshexpmatch=False):

	fobjList = []
	domainsDict = defaultdict(lambda:[])
	domainsDict['com'] = defaultdict(lambda:[])
	domainsDict['org'] = defaultdict(lambda:[])
	domainsDict['net'] = defaultdict(lambda:[])
	outputhandle = open(output, 'wb')

	try:

		if fetchgfwlist:
			resp = urllib2.urlopen(GFWLIST_URL)
			fobjList.append(StringIO(base64.b64decode(resp.read())))
		for i in inputs:
			fobjList.append(open(i))

		domains, searches = parse_gfwlist_content(chain(*fobjList))

		for l in domains:
			if suffixPtn.search(l):
				xs = l.split('.')
				if xs[-1] in ['com', 'org', 'net']:
					domainsDict[xs[-1]][xs[-2][-1]].append(l)
				else:
					domainsDict[xs[-1]].append(l)
			else:
				domainsDict['unknown'].append(l)

		tl = string.Template(PAC_VAR)
		outputhandle.write(tl.substitute({
			'proxy':proxy,
			'domains':json.dumps(domainsDict),
			'search':json.dumps(tuple(i for i in searches), indent=1)}))
		outputhandle.write('\n')
		if hasshexpmatch:
			outputhandle.write(SHEXPMATCH)
			outputhandle.write('\n')
		outputhandle.write(PAC_FUNC)

	finally:
		for i in fobjList:
			i.close()
		outputhandle.close()


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()

	parser.add_argument('-t', '--proxy-type', choices=['PROXY', 'SOCKS5', 'SOCKS4', 'SOCKS'], dest='proxy', default='SOCKS5',help='proxy server type, use PROXY(http) or SOCKS5 (default: SOCKS5)')
	parser.add_argument('-a', '--proxy-addr', dest='addr', default='127.0.0.1', help='proxy server address (default: 127.0.0.1)')
	parser.add_argument('-p', '--proxy-port', dest='port', type=int, required=True, help='proxy server listening port')
	parser.add_argument('-g', '--fetch-gfwlist', action='store_true', dest='fetchgfwlist', default=False, help='fetch gfwlist from <{0}>'.format(GFWLIST_URL))
	parser.add_argument('-s', '--shexpmatch', action='store_true', dest='shexpmatch', default=False, help='use own shExpMatch, instead of depending on the host implementation')
	parser.add_argument('-o', '--output', dest='output', default='autoconfig.pac', help='output file (default: autoconfig.pac)')
	parser.add_argument('USERFILE', nargs='*', help='user provided gfwlist compatible file(s)')

	args = parser.parse_args()

	if not args.fetchgfwlist and len(args.USERFILE) == 0:
		raise SystemExit('nothing to do')

	proxy = {
	'SOCKS5':'{0} {1}:{2};',
	'SOCKS4':'{0} {1}:{2};',
	'SOCKS':'{0} {1}:{2}',
	'PROXY':'{0} {1}:{2}'}[args.proxy].format(args.proxy, args.addr, args.port)

	main(args.USERFILE, args.output, proxy, args.fetchgfwlist, args.shexpmatch)
