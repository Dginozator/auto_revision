import cv2
import numpy as np

import pytesseract

import re

import glob
import os
from datetime import datetime as DT, timedelta

pytesseract.pytesseract.tesseract_cmd = 'C:\\e_programs\\tesseract\\tesseract.exe'

patterns = [
	'patterns\\food_1k.png',
	'patterns\\food_3k.png',
	'patterns\\food_5k.png',
	'patterns\\food_10k.png',
	'patterns\\wood_1k.png',
	'patterns\\wood_3k.png',
	'patterns\\wood_5k.png',
	'patterns\\wood_10k.png',
	'patterns\\iron_1k.png',
	'patterns\\iron_2k.png',
	'patterns\\iron_100k.png',
	'patterns\\silver_250.png',
	'patterns\\silver_500.png',
	'patterns\\silver_25k.png'
]

def readImageText3(pImage):
	lConfig = r'--psm 7 --oem 3 -c tessedit_char_whitelist=.,0123456789K'

	scale_percent_x = 400
	scale_percent_y = 400
	width = int(pImage.shape[1] * scale_percent_x / 100)
	height = int(pImage.shape[0] * scale_percent_y / 100)
	dim = (width, height)

	pImage = cv2.resize(pImage, dim, interpolation = cv2.INTER_AREA)

	gray = cv2.cvtColor(pImage, cv2.COLOR_BGR2GRAY)
	gray = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	gray = cv2.bitwise_not(gray)
	
	for i in range(5, 15):
		i = 11
		strToPrint = '%d| ' % i
		for j in range(2, 10):
			j = 3
			kernel = np.ones((i,i),np.uint8)
			testImg = cv2.erode(gray,kernel,iterations = 1)
			kernel = np.ones((j,j),np.uint8)
			testImg = cv2.dilate(testImg,kernel,iterations = 1)

			res = pytesseract.image_to_string(testImg, lang='eng', config=lConfig)
			res = res.split('\n')[0]
			strToPrint += "%s|" % (res)
			break
		break
	return res

# good for text
def readImageText2(pImage):
	config = r'--oem 3 --psm 6'
	text = ''
	img = cv2.cvtColor(pImage, cv2.COLOR_BGR2GRAY)

	scale_percent_x = 50
	scale_percent_y = 100
	width = int(img.shape[1] * scale_percent_x / 100)
	height = int(img.shape[0] * scale_percent_y / 100)
	dim = (width, height)

	img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
	img = cv2.bitwise_not(img)

	text = pytesseract.image_to_string(img, lang='eng', config=config)
	text = text.split('\n')[0]

	return text

def isLordScreen(pFullImage):
	cropImg = pFullImage[10:70, 200:508]
	return((readImageText2(cropImg)).find('LORD') != -1)

def profileName(pFullImage, pFileName, pGame = 'GoG'):
	patternName = 'patterns\\copy_nick.png'
	method = cv2.TM_CCOEFF_NORMED

	name = ''

	pattern = cv2.imread(patternName, 0)

	imgColor = pFullImage
	img = cv2.imread(pFileName, 0)

	w, h = pattern.shape[::-1]
	text_h = 31
	shift_x = -260

	match = cv2.matchTemplate(img,pattern,method)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
	top_left = max_loc
	bottom_right = (top_left[0] + w, top_left[1] + h)
	if (max_val > 0.9):
		top_left_text = (top_left[0] + shift_x, top_left[1])
		bottom_right_text = (top_left[0], top_left[1] + h)

		cropped_image = imgColor[top_left_text[1]:bottom_right_text[1], top_left_text[0]:bottom_right_text[0]]

		name = readImageText2(cropped_image)

	return (name)

def isResScreen(pFullImage):
	# cropImg = pFullImage[28:60, 347:593]
	cropImg = pFullImage[28:60, 237:593]

	return((readImageText2(cropImg)).find('INVENTORY') != -1)

def typeScreen(pFullImage):
	types = {'lord':'lord',
						'res':'res',
						'other':'other'}
	if (isLordScreen(pFullImage)):
		rType = types['lord']
	elif (isResScreen(pFullImage)):
		rType = types['res']
	else:
		rType = types['other']
	return (rType)

def parseGold(pFullImage):
	gold = -1

	# 1757, 24 - 1910, 62
	cropImg = pFullImage[24:62, 1757:1910]

	gold = readImageText2(cropImg)
	gold = gold.replace(',','')
	if (lparseInt(gold) is None):
		gold = -1

	return (gold)

def lparseInt(sin):
  import re
  m = re.search(r'(\d+)[.,]?\d*?', str(sin))
  return int(m.groups()[-1]) if m and not callable(sin) else None

def scrList():
	filesList = []
	sortedFiles = []
	path = '../src/*.*'
	files = glob.glob(os.path.expanduser(path))
	for f in files:
		ctime = (re.search(r'[\d-]+', f))[0]
		dt_fmt = '%Y-%m-%d-%H-%M-%S-%f'
		ctime = DT.strptime(ctime, dt_fmt)
		filesList.append({'name': f, 'ctime': ctime})

	sortedFiles = sorted(filesList, key=lambda t: t['ctime'])

	return sortedFiles

def readRes(pImg, pFileName, pGame='GoG'):
	res = {}
	method = cv2.TM_CCOEFF_NORMED
	errors = 0

	imgColor = pImg
	img = cv2.imread(pFileName, 0)

	lpatterns = patterns

	for patternName in lpatterns:
		patternLabel = (re.search(r'[^\\]+\.png$', patternName))[0]
		patternLabel = patternLabel.replace('.png', '')

		pattern = cv2.imread(patternName, 0)
		w, h = pattern.shape[::-1]
		margin = 6
		text_h = 31
		margin_h = 0

		match = cv2.matchTemplate(img,pattern,method)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
		top_left = max_loc
		bottom_right = (top_left[0] + w, top_left[1] + h)

		top_left_text = (top_left[0] - margin, top_left[1] + h + 2 + margin_h)
		bottom_right_text = (bottom_right[0] + margin, top_left_text[1] + text_h)
		if (max_val > 0.9):
			cropped_image = imgColor[top_left_text[1]:bottom_right_text[1], top_left_text[0]:bottom_right_text[0]]

			lot_count = readImageText3(cropped_image).replace(',','.')
			try:
				cropped_image = textaboveImg(cropped_image, lot_count)
				lot_count = [lot_count, cropped_image]
				res.update([(patternLabel, lot_count)])
			except:
				errors += 1
				res.update(errors=errors)
	return (res)

def stackImgs(a, b, orient = 'h'):
	ha,wa,ca = a.shape
	hb,wb,cb = b.shape
	
	wmargin = 10
	hmargin = 10

	c = a

	if (orient=='h'):
		h = max([ha,hb])
		if (ha >= hb):
			size = h, wb, 3
			m = np.zeros(size, dtype=np.uint8)
			m[(h-hb):h, 0:wb] = b
			b = m
		else:
			size = h, wa, 3
			m = np.zeros(size, dtype=np.uint8)
			m[(h-ha):h, 0:wa] = a
			a = m
		size = h,wmargin,3
		marginArea = np.zeros(size, dtype=np.uint8)
		c = np.hstack((a,marginArea,b))
	else:
		w = max([wa,wb])
		if (wa >= wb):
			size = hb, w, 3
			m = np.zeros(size, dtype=np.uint8)
			m[0:hb, 0:wb] = b
			b = m
		else:
			size = ha, w, 3
			m = np.zeros(size, dtype=np.uint8)
			m[0:ha, 0:wa] = a
			a = m
		size = hmargin,w,3
		marginArea = np.zeros(size, dtype=np.uint8)
		c = np.vstack((a,marginArea,b))
	return c

def textaboveImg(pImg, text):
	text = str(text)

	# similar fonts: 2, 6, 0
	font                   	= 2
	fontScale              	= 1
	# BGR format
	fontColor              	= (0,255,0)
	thickness 							= 2

	(text_width, text_height) = cv2.getTextSize(text, font, fontScale=fontScale, thickness=1)[0]

	try:
		h,w,c = pImg.shape
	except:
		w = text_width

	img = np.zeros((text_height + 6,w,3), np.uint8)
	if (pImg is not None):
		img = stackImgs(img, pImg, orient = 'v')

	bottomLeftCornerOfText 	= (w-text_width, text_height+6)

	cv2.putText(img,text, 
		bottomLeftCornerOfText, 
		font, 
		fontScale,
		fontColor,
		thickness)
	
	return img

def resBookToCSV(pBook):
	sep = ';'
	header = 'game;lord;food_1k;food_3k;food_5k;food_10k;wood/oil_1k;wood/oil_3k;wood/oil_5k;wood/oil_10k;iron_1k;iron_2k;iron_100k;silver/alloy_250;silver/alloy_500;silver/alloy_25k;errors'
	csv = header + '\n'

	headerList = {
		'GoG': [
			'food_1k',
			'food_3k',
			'food_5k',
			'food_10k',
			'wood_1k',
			'wood_3k',
			'wood_5k',
			'wood_10k',
			'iron_1k',
			'iron_2k',
			'iron_100k',
			'silver_250',
			'silver_500',
			'silver_25k'
		]
	}

	lstr = ''
	graph = None

	for g, book in pBook.items():
		for lord, res in book.items():
			lstr = g
			lstr += sep + lord
			graphstr = textaboveImg(None, g + '_' + lord)
			for r in headerList[g]:
				if (r in res):
					graphstr = stackImgs(graphstr, res[r][1], orient = 'h')
					lstr += sep + str(res[r][0])
				else:
					lstr += sep + ''
			if (graph is None):
				graph = graphstr
			else:
				graph = stackImgs(graph, graphstr, orient = 'v')

			lstr += sep + str(res.get('errors', 0))
			csv += lstr + '\n'

	# if (graph is not None):
	# 	cv2.imshow("img",graph)
	# 	cv2.waitKey(0)
	# 	cv2.destroyAllWindows()

	return csv, graph

def main():
	filesList = scrList()
	games = {	'GoG':'GoG'}
	game = ''
	lordName = ''
	res = 0
	resBook = {'GoG':{}}
	otherPages = 0
	for f in filesList:
		filename = f['name']
		print(filename)
		img = cv2.imread(filename)
		typeScr = typeScreen(img)
		if typeScr == 'lord':
			game = games['GoG']
			lordName = profileName(img, filename)
		elif (typeScr == 'res'):
			if lordName == '':
				continue
			res = readRes(img, filename, pGame = game)
			if resBook[game].get(lordName):
				if 'errors' in resBook[game][lordName]:
					errs = resBook[game][lordName]['errors']
					resBook[game][lordName].update(res)
					resBook[game][lordName]['errors'] += errs
				else:
					resBook[game][lordName].update(res)
			else:
				resBook[game].update([(lordName, res)])
			# print (resBook)
			csv, graph = resBookToCSV(resBook)
			print (csv)
		else:
			otherPages += 1
			print (typeScr)
			print ('other pages: %d' % otherPages)
	csv, graph = resBookToCSV(resBook)
	with open('book.csv', 'w') as f:
		print ('create file book.csv')
		f.write(csv)
	print ('create file book.png')
	cv2.imwrite('book.png', graph)
	return

# img = cv2.imread('sample.png')
# profileName (img, 'scr\\Screenshot_2020-12-29-06-54-34-432_com.diandian.gog.png')

main()

# textaboveImg(img, "20610")

# print('for test 1812')
# print(scrList())

#src = '../src/2021-12-30-02-13-14-028502.png'
#img = cv2.imread(src)
#r = readRes(img, src)
#for key in r:
#	r[key] = r[key][0]
#print (r)
#print (r['errors'])

#!!! if no correct figure - print figures anymore