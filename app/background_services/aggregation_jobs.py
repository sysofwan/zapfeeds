import logging

from app.background_services.aggregation.main import get_primary_content_data
from app.models.content_metadata import ContentSource
from app.models.Content import Content
from app.background_services.ranking.social_data import get_social_share, get_total_shares
from app import db
from app.background_services.ranking.rank import rank_content

session = db.session
logger = logging.getLogger(__name__)

def update_contents():
    aggregate_content()
    populate_social_count()
    rank_contents()
    populate_real_shares()

def aggregate_content():
    logger.info('Aggregating contents...')
    sources = ContentSource.get_all_sources()
    for source in sources:
        get_primary_content_data(source.url, source.id, session)

def populate_social_count():
    logger.info('Populating social counts...')
    contents = Content.get_unranked_contents_by_age(1)
    for content in contents:
        try:
            social_share = get_social_share(content.url)
        except Exception as e:
            logger.error('Unable to fetch social count for content with id: %s. %s, %s',
                         content.id, e.__class__.__name__, e.message)
            continue
        social_share.content_id = content.id
        session.add(social_share)
        session.add(content)
    session.commit()

def populate_real_shares():
    logger.info('Populating real shares...')
    contents = Content.get_content_no_real_shares_by_age(3)
    for content in contents:
        total_share = get_total_shares(content.url)
        content.real_shares = total_share
        session.add(content)
    session.commit()

def rank_contents():
    logger.info('Ranking contents...')
    contents = Content.get_content_for_ranking(3)
    for content in contents:
        content.rank = rank_content(content)
        session.add(content)
    session.commit()

