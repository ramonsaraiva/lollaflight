import re
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup as bs

from flask import jsonify

from flask.ext.restful import Resource
from flask.ext.restful import reqparse

from models import db
from models import Flight
from models import Survey

GOL_FORM_STR = 'ControlGroupSearchView$AvailabilitySearchInputSearchView$'
GOL_TYPES = {
	'text': 'TextBoxMarket',
	'radio': 'RadioButtonMarket',
	'dropdown': 'DropDownListMarket',
	'dropdown_p': 'DropDownListPassengerType_'
}

def to_float(s):
	return float(s.replace('.', '').replace(',', '.'))

def gol_form(itype, name):
	return '{0}{1}{2}'.format(GOL_FORM_STR, GOL_TYPES[itype], name)

def gol_data():
	s = requests.Session()
	r = s.get('http://www.voegol.com.br/pt-br/paginas/default.aspx')

	orig = 'Porto+Alegre+(POA)'
	dest = 'Sao+Paulo+-+Congonhas+(CGH)'

	cookies = {
		'origem': 'POA',
		'destino': 'CGH'
	}

	form = {
		'ctl00$PlaceHolderMain$origem': orig,
		'ctl00$PlaceHolderMain$para': dest,
		gol_form('radio', 'Structure'): 'RoundTrip',
		gol_form('text', 'Origin1'): 'POA',
		gol_form('text', 'Destination1'): 'CGH',
		gol_form('dropdown', 'Day1'): '11',
		gol_form('dropdown', 'Month1'): '2016-03',
		gol_form('dropdown', 'Day2'): '14',
		gol_form('dropdown', 'Month2'): '2016-03',
		gol_form('dropdown_p', 'ADT'): '2',
		gol_form('dropdown_p', 'CHD'): '0',
		gol_form('dropdown_p', 'INFT'): '0',
		gol_form('dropdown', 'ResidentCountry'): 'BR',
		gol_form('dropdown', 'SearchBy'): 'columnView',
		'ControlGroupSearchView$AvailabilitySearchInputSearchView$flightStatusDate': '10/10/2015',
		'PageFooter_SearchView$DropDownListOriginCountry': 'pt',
		'ControlGroupSearchView$ButtonSubmit': 'compre+aqui',
		'__EVENTARGUMENT': '',
		'__EVENTTARGET': ''
	}

	r = s.post('http://compre2.voegol.com.br/CSearch.aspx?culture=pt-br', data=form, cookies=cookies)
	return bs(r.text, 'html.parser')

def gol_parse(data):
	going, back = data.findAll('div', {'class': 'ContentTable'})

	flights_going = going.findAll('div', {'class': 'lineTable'})
	flights_back =  back.findAll('div', {'class': 'lineTable'})

	going = []
	back = []

	reg = '(\d+.)*\d+,\d+'

	for flight in flights_going:
		f = {}
		f['name'] = flight.find('span', {'class': 'operatedBy'}).text[:7]
		f['time_going'] = flight.find('span', {'class': 'timeGoing'}).text
		f['time_back'] = flight.find('span', {'class': 'timeoutGoing'}).text
		f['scales'] = flight.find('span', {'class': 'plusBus'}).text

		price = 9999

		try:
			price = to_float(re.search(reg, flight.find('div', {'class': 'taxa taxaFlexivel'}).find('strong', {'class': 'fareValue'}).text).group(0))
		except:
			pass

		try:
			prog = to_float(re.search(reg, flight.find('div', {'class': 'taxa taxaProgramada'}).find('strong', {'class': 'fareValue'}).text).group(0))
			if prog < price:
				price = prog
		except:
			pass

		try:
			promo = to_float(re.search(reg, flight.find('div', {'class': 'taxa taxaPromocional'}).find('strong', {'class': 'fareValue'}).text).group(0))
			if promo < price:
				price = promo
		except:
			pass

		f['price'] = price

		going.append(f)

	for flight in flights_back:
		f = {}
		f['name'] = flight.find('span', {'class': 'operatedBy'}).text[:7]
		f['time_going'] = flight.find('span', {'class': 'timeGoing'}).text
		f['time_back'] = flight.find('span', {'class': 'timeoutGoing'}).text
		f['scales'] = flight.find('span', {'class': 'plusBus'}).text

		price = 9999

		try:
			price = to_float(re.search(reg, flight.find('div', {'class': 'taxa taxaFlexivel'}).find('strong', {'class': 'fareValue'}).text).group(0))
		except:
			pass

		try:
			prog = to_float(re.search(reg, flight.find('div', {'class': 'taxa taxaProgramada'}).find('strong', {'class': 'fareValue'}).text).group(0))
			if prog < price:
				price = prog
		except:
			pass

		try:
			promo = to_float(re.search(reg, flight.find('div', {'class': 'taxa taxaPromocional'}).find('strong', {'class': 'fareValue'}).text).group(0))
			if promo < price:
				price = promo
		except:
			pass

		f['price'] = price
		back.append(f)

	return going, back

def tam_data():
	s = requests.Session()
	d = s.get('http://www.tam.com.br')
	p = bs(d.text, 'html.parser')

	cookies = {
	}
	
	form = {
		'WDS_CORPORATE_SALES': 'FALSE',
		'SITE': 'JJBKJJBK',
		'LANGUAGE': 'BR',
		'WDS_MARKET': 'BR',
		'FROM_PAGE': 'HOME_SEARCH',
		'B_DATE_1': '201603110000',
		'B_DATE_2': '201603140000',
		'B_LOCATION_1': 'POA',
		'E_LOCATION_1': 'CGH',
		'WDS_FORCE_SITE_UPDATE': 'TRUE',
		'FORCE_OVERRIDE': 'TRUE',
		'TRIP_TYPE': 'R',
		'search_from': 'Porto+Alegre+-+Salgado+Filho+Internacional+(POA)',
		'search_to': 'Sao+Paulo+-+Congonhas+(CGH)',
		'adults': '2',
		'children': '0',
		'infants': '0',
		'CORPORATE_CODE_INPUT': '',
		'SEACH_COOKIE': '"{"bounds":[null,null,null,null,null,null,null,null,null,null,{"bLocation":"POA","eLocation":"CGH","bDate":"201603110000"},{"bDate":"201603140000"}],"roundtripCommon":{"tripType":"R","adults":"2","children":"0","infants":"0","mcabin":null}}"'
	}

	d = s.post('http://book.tam.com.br/TAM/dyn/air/booking/upslDispatcher;jsessionid=dh9csky6V5pDct8lcQcV_TZaedKzD6Z2LOj4Gg8GH5qvYoRIRXp_!1618028954!549751287', data=form)
	p = bs(d.text, 'html.parser')
	return p

def tam_parse(data):
	going_data = data.find('table', {'id': 'outbound_list_flight'})
	back_data = data.find('table', {'id': 'inbound_list_flight'})

	going = []
	back = []

	for flight in going_data.findAll('tr', {'class': 'flightType-Direct'}):
		f = {}

		tds = flight.findAll('td')
		f['time_going'] = tds[0].find('strong').text
		f['time_back'] = tds[1].find('strong').text
		f['name'] = tds[2].find('a').text
		basic = float(tds[4]['data-cell-value'])
		flex = float(tds[5]['data-cell-value'])
		top = float(tds[6]['data-cell-value'])
		f['price'] = min([basic, flex, top])
		f['scales'] = 'Voo direto'

		going.append(f)

	for flight in back_data.findAll('tr', {'class': 'flightType-Direct'}):
		f = {}
		tds = flight.findAll('td')
		f['time_going'] = tds[0].find('strong').text
		f['time_back'] = tds[1].find('strong').text
		f['name'] = tds[2].find('a').text
		basic = float(tds[4]['data-cell-value'])
		flex = float(tds[5]['data-cell-value'])
		top = float(tds[6]['data-cell-value'])
		f['price'] = min([basic, flex, top])
		f['scales'] = 'Voo direto'

		back.append(f)
	return (going, back)

class Surveys(Resource):
	def get(self):
		return [s.serialize for s in Survey.query.order_by(Survey.date.desc()).limit(5)]

class Check(Resource):
	def post(self):
		going_gol, back_gol = gol_parse(gol_data())
		going_tam, back_tam = tam_parse(tam_data())

		s = Survey()
		s.date = datetime.now()
		for flight in going_gol:
			f = Flight(flight, True)
			f.company = 'GOL'
			s.flights.append(f)
		for flight in back_gol:
			f = Flight(flight, False)
			f.company = 'GOL'
			s.flights.append(f)

		for flight in going_tam:
			f = Flight(flight, True)
			f.company = 'TAM'
			s.flights.append(f)
		for flight in back_tam:
			f = Flight(flight, False)
			f.company = 'TAM'
			s.flights.append(f)

		db.session.add(s)
		db.session.commit()
		return s.serialize
