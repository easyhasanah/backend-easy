import joblib
from flask import Blueprint, jsonify, request
from app.models import db, HasanahCards
from app.services.jwt import token_required
from datetime import datetime, timedelta
import random

hasanahCards_bp = Blueprint('hasanah_cards', __name__, url_prefix='/api/card')

@hasanahCards_bp.route('/', methods=['GET'])
@token_required
def get_card(user_id):
    submission = HasanahCards.query.filter_by(user_id=user_id).first_or_404()
    return jsonify(submission.to_dict())

@hasanahCards_bp.route('/', methods=['POST'])
@token_required
def add_card(user_id):
    feature_input = request.get_json()

    expired_date_data = datetime.utcnow().date().replace(year=datetime.utcnow().year + 5)
    card_no_data = ''.join([str(random.randint(0, 9)) for _ in range(16)])

    card = HasanahCards(
        card_no = card_no_data,
        expired_date = expired_date_data,
        user_id = user_id,
        pin = feature_input['pin'],
        card_category_id = int(feature_input['card_category'])
    )

    db.session.add(card)
    db.session.commit()

    return jsonify({'message': 'Card inserted successfully'}), 201