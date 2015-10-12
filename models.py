from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Flight(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	survey_id = db.Column(db.Integer, db.ForeignKey('survey.id', ondelete='CASCADE'), nullable=False)
	name = db.Column(db.String(8))
	going = db.Column(db.Boolean())
	time_going = db.Column(db.String(8))
	time_back = db.Column(db.String(8))
	scales = db.Column(db.String(32))
	price = db.Column(db.Numeric(precision=9, scale=2))
	company = db.Column(db.String(3))

	def __init__(self, data, going):
		self.name = data['name']
		self.going = going
		self.time_going = data['time_going']
		self.time_back = data['time_back']
		self.scales = data['scales']
		self.price = data['price']

	@property
	def serialize(self):
		return {
			'name': self.name,
			'time_going': self.time_going,
			'time_back': self.time_back,
			'scales': self.scales,
			'price': float(self.price)
		}

class Survey(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime())
	flights = db.relationship('Flight', backref='survey', lazy='dynamic', cascade='all, delete-orphan')

	@property
	def best_prices(self):
		best_going_gol = 99999
		best_back_gol = 99999
		best_going_tam = 99999
		best_back_tam = 99999

		for f in [f for f in self.flights if f.company == 'GOL']:
			if f.going:
				if f.price < best_going_gol:
					best_going_gol = f.price
				continue
			if f.price < best_back_gol:
				best_back_gol = f.price

		for f in [f for f in self.flights if f.company == 'TAM']:
			if f.going:
				if f.price < best_going_tam:
					best_going_tam = f.price
				continue
			if f.price < best_back_tam:
				best_back_tam = f.price

		return {'gol': (float(best_going_gol), float(best_back_gol)), 'tam': (float(best_going_tam), float(best_back_tam))}

	@property
	def serialize_flights(self):
		return {
			'gol': {
				'going': [f.serialize for f in self.flights if f.going and f.company == 'GOL'],
				'back': [f.serialize for f in self.flights if not f.going and f.company == 'GOL']
			},
			'tam': {
				'going': [f.serialize for f in self.flights if f.going and f.company == 'TAM'],
				'back': [f.serialize for f in self.flights if not f.going and f.company == 'TAM']
			}
		}

	@property
	def serialize(self):
		return {
			'id': self.id,
			'date': self.date.strftime('%d/%m/%y %I:%M%p'),
			'flights': self.serialize_flights,
			'best_prices': self.best_prices
		}
