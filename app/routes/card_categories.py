import joblib
from flask import Blueprint, jsonify, request
from app.models import db, CardCategories
from app.services.jwt import token_required

cardCategories_bp = Blueprint('card_categories', __name__, url_prefix='/api/card-categories')

@cardCategories_bp.route('/', methods=['GET'])
@token_required
def get_card_category_by_id(card_category_id):
    category_id = request.args.get('category_id', type=int)
    card_categories = CardCategories.query.filter_by(id=category_id).first_or_404()
    return jsonify(card_categories.to_dict())