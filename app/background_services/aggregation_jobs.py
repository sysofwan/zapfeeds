import logging
import time
from datetime import timedelta

from ranking.predict_social_shares import *
from app.background_services.aggregation.main import get_primary_content_data
from app.models.content_metadata import ContentSource
from app.models.Content import Content
from app.background_services.ranking.social_data import get_social_share, get_total_shares
from app import db
from app.background_services.ranking.rank import rank_content
from app.background_services.ranking.cluster import cluster_news, update_parent_cluster

session = db.session
logger = logging.getLogger(__name__)


def update_contents():
    aggregate_content()
    #discussion on how to display the clusters
    cluster_content()
    populate_social_count()
    rank_contents()
    populate_real_shares()
    #update 'scoreboard'


def aggregate_content():
    logger.info('starting content aggregation...')
    start_time = time.time()
    sources = ContentSource.get_all_sources()
    for source in sources:
        get_primary_content_data(source.url, source.id, session)
    logger.info('content aggregation completed in %s', str(timedelta(seconds=time.time() - start_time)))


def cluster_content():
    """
    @processes:
    1.get data: new content + top n contents
    2.cluster
    3.determine parent cluster
    4.update parent cluster
    5.store results

    @todo:
    1.use better feature vectorizer (word2vec?)
    2.display the cluster
    """
    logger.info('starting clustering sequence...')
    start_time = time.time()
    contents = Content.get_content_for_clustering()
    clusters = cluster_news(contents, train=True)
    update_parent_cluster(clusters, contents, session)
    logger.info('clustering completed in %s', str(timedelta(seconds=time.time() - start_time)))


def populate_social_count():
    logger.info('starting social count population...')
    start_time = time.time()
    contents = Content.get_unranked_contents_by_age(1)
    for content in contents:
        try:
            social_share = get_social_share(content.url)
        except Exception:
            logger.exception('Unable to fetch social count for content with id: %s.',
                         content.id)
            continue
        social_share.content_id = content.id
        content.predicted_shares = predicted_shares(social_share, content)
        session.add(social_share)
        session.add(content)
    session.commit()
    logger.info('social count population completed in %s', str(timedelta(seconds=time.time() - start_time)))


def populate_real_shares():
    logger.info('starting real shares population...')
    start_time = time.time()
    contents = Content.get_content_no_real_shares_by_age(3)
    for content in contents:
        try:
            total_share = get_total_shares(content.url)
        except Exception:
            logger.exception('Unable to fetch real shares for content with id %s', content.id)
            continue
        content.real_shares = total_share
        session.add(content)
    session.commit()
    logger.info('real shares population completed in %s', str(timedelta(seconds=time.time() - start_time)))


def rank_contents():
    logger.info('starting content ranking...')
    start_time = time.time()
    contents = Content.get_content_for_ranking(3)
    for content in contents:
        content.rank = rank_content(content)
        session.add(content)
    session.commit()
    logger.info('ranking completed in %s', str(timedelta(seconds=time.time() - start_time)))


def update_aggregated_data():
    """
    1.data w/ real_shares:
    2.extract data:
    3.update:
    """
    pass




