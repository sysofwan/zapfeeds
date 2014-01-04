from flask import Blueprint, request, jsonify
from app.models.Content import Content
from app.models.contentMeta import Tag
import json
import urllib2
import datetime
import time

rest = Blueprint('rest', __name__, url_prefix='/rest')


@rest.route('/content/topcontent', methods=['GET'])
def get_top_content():
    valid_cookie = is_cookie_valid()
    history = get_history() if valid_cookie else []
    page_no = get_page_no() if valid_cookie else None
    if len(history) < 360:
        contents = [content.fp_serialize for content in Content.get_top_unviewed(history)]
    else:
        if not page_no:
            page_no = 1
        contents = [content.fp_serialize for content in Content.get_top_by_pages(page_no, history)]
    response = jsonify({'results': contents})
    if not valid_cookie:
        reset_cookie(response)
    set_cookie_time(response)
    return response

@rest.route('/content/filter/<int:page>', methods=['GET'])
def get_filtered_content(page):
    types = request.args.getlist('type')
    tags = request.args.getlist('tag')
    contents = []
    if tags:
        contents.extend([content.fp_serialize for content in Content.get_top_tag_filtered(page, tags)])
    if types:
        contents.extend([content.fp_serialize for content in Content.get_top_type_filtered(page, types)])
    response = jsonify({'results': contents})
    return response


@rest.route('/meta/alltags', methods=['GET'])
def get_all_tags():
    tags = [tag.tag_string for tag in Tag.get_all_tags()]
    return jsonify({'results': tags})


def get_page_no():
    page = request.cookies.get('page')
    if page and page.isdigit():
        return int(page)
    else:
        return None


def get_history():
    try:
        history = json.loads(urllib2.unquote(request.cookies.get('view_history', '%5B%5D')))
    except:
        history = []
    return history


def is_cookie_valid():
    expire_time = request.cookies.get('expr_usr')
    curr_time = time.mktime(datetime.datetime.now().timetuple())
    if expire_time:
        return curr_time < int(expire_time)
    return False


def reset_cookie(response):
    response.set_cookie('view_history', '%5B%5D')
    response.set_cookie('page', '0')


def set_cookie_time(response):
    # Six hours since last visit expire time (to change)
    expire_time = int(time.mktime(datetime.datetime.now().timetuple())) + (6 * 60 * 60)
    response.set_cookie('expr_usr', str(expire_time))


