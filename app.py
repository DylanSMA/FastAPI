from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
import os

# Création de l'instance de l'app Flask
app = Flask(__name__)

# Config de l'URI (Uniform Resource Identifier) de la bdd SQLite

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # Emplacement de la bdd
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Désactive le suivi des modifications

db = SQLAlchemy(app) # Instance SQLAlchemy
api = Api(app) # Instance API Flask Restful

# Création des définitions du modèle de données pour store les data
class EventModel(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Identifiant unique de l'évènement
    name = db.Column(db.String(80), nullable=False) # Nom de l'évent
    date = db.Column(db.String(20), nullable=False) # Date de l'event
    type = db.Column(db.String(80), nullable=False) # Type de l'évent
    game = db.Column(db.String(80), nullable=False) # Game de l'évent
    description = db.Column(db.String(100), nullable=False) # Description de l'event
    def __repr__(self):
        return f"Event(name = {self.name}, date = {self.date}, type = {self.type}, game = {self.game}, description = {self.description})"

# Definir de nouveaux arguments :
event_args = reqparse.RequestParser() # Validé les données reçu
event_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
event_args.add_argument('date', type=str, required=True, help="Date cannot be blank")
event_args.add_argument('type', type=str, required=True, help="Type cannot be blank")
event_args.add_argument('game', type=str, required=True, help="Game cannot be blank")
event_args.add_argument('description', type=str, required=True, help="Description cannot be blank")

eventFields = {
    'id':fields.Integer,
    'name':fields.String,
    'date':fields.String, 
    'type':fields.String,
    'game':fields.String,
    'description':fields.String,  
}

class Events(Resource):
    @marshal_with(eventFields)
    def get(self):
        events = EventModel.query.all()
        return events
    @marshal_with(eventFields)
    def post(self):
        args = event_args.parse_args()
        event = EventModel(name=args["name"], date=args["date"], type=args["type"],game=args["game"], description=args["description"])
        db.session.add(event)
        db.session.commit()
        events = EventModel.query.all() # Récupère tous les évènements
        return events, 201

# Récupérez les event à partir des id        
class Event(Resource):
   @marshal_with(eventFields)
   def get(self, id):
       event = EventModel.query.filter_by(id=id).first()
       if not event:
           abort(404, "Event not Found")
       return event
   # Pour modifier/remplacer des évènements déjà dans la database
   @marshal_with(eventFields)
   def patch(self, id):
       args = event_args.parse_args()
       event = EventModel.query.filter_by(id=id).first()
       if not event:
           abort(404, "Event not Found")
    #Update la database
       event.name = args["name"]
       event.date = args["date"]
       event.type = args["type"]
       event.game = args["game"]
       event.description = args["description"]
       db.session.commit()
       return event
   #Delete dans la database
   @marshal_with(eventFields)
   def delete(self, id):
       event = EventModel.query.filter_by(id=id).first()
       if not event:
           abort(404, "Event not Found")
       db.session.delete(event)
       db.session.commit()
       events = EventModel.query.all() # Récupère tous les évènements
       return events

# Ajout des ressources API, endpoints :
api.add_resource(Events, '/events')
api.add_resource(Event, '/events/<int:id>')

# Création des tables dans la base de données :
with app.app_context():
    db.create_all() # Créer la Database   

# Supprime le fichier de database s'il existe déjà
if os.path.exists('database.db'):
    os.remove('database.db')
 
# Route pour la page d'accueil   
@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

# Point d'entrée de l'application
if __name__ == '__main__':
    app.run(debug=True)