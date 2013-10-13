from flask import Blueprint, request, jsonify
from app.models.Content import Content

rest = Blueprint('rest', __name__, url_prefix='/rest')

@rest.route('/content/topcontent', methods=['GET'])
def get_top_content():
    start_idx = request.args.get('start_idx', 0)
    end_idx = request.args.get('end_idx', start_idx + 30)
    contents = Content.get_front_page_in_range(start_idx, end_idx)
    return jsonify({'results': [content.fp_serialize for content in contents], 'startIdx': start_idx, 'endIdx': end_idx})


