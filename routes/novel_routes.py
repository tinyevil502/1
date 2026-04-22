from flask import Blueprint, request
from sqlalchemy import or_
from models.db import SessionLocal, NovelInfo
from utils.response import make_response, error_response
from utils.text_utils import truncate_text
from utils.logger import get_logger

logger = get_logger(__name__)

novels_bp = Blueprint('novels', __name__)


@novels_bp.route('/novels', methods=['GET'])
def get_novels():
    db = SessionLocal()
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        category = request.args.get('category', '')
        status = request.args.get('status', '')
        keyword = request.args.get('keyword', '')

        query = db.query(NovelInfo)

        if category:
            query = query.filter(NovelInfo.category_name == category)
        if status:
            query = query.filter(NovelInfo.status == status)
        if keyword:
            query = query.filter(
                or_(
                    NovelInfo.novel_name.like(f'%{keyword}%'),
                    NovelInfo.author_name.like(f'%{keyword}%')
                )
            )

        total = query.count()
        novels = query.offset((page - 1) * size).limit(size).all()

        items = [
            {
                'id': n.id,
                'novel_name': n.novel_name,
                'author_name': n.author_name,
                'category_name': n.category_name,
                'status': n.status,
                'word_count': n.word_count,
                'update_time': n.update_time,
                'intro': truncate_text(n.intro, 100) if n.intro else '',
                'source_url': n.source_url,
            }
            for n in novels
        ]

        return make_response(True, {
            'page': page,
            'size': size,
            'total': total,
            'items': items
        }, 'OK')
    except Exception as e:
        logger.error(f"get_novels failed: {e}")
        return error_response(str(e))
    finally:
        db.close()


@novels_bp.route('/novels/search', methods=['GET'])
def search_novels():
    db = SessionLocal()
    try:
        q = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))

        query = db.query(NovelInfo)

        if q:
            query = query.filter(
                or_(
                    NovelInfo.novel_name.like(f'%{q}%'),
                    NovelInfo.author_name.like(f'%{q}%'),
                    NovelInfo.intro.like(f'%{q}%')
                )
            )
        if category:
            query = query.filter(NovelInfo.category_name == category)
        if status:
            query = query.filter(NovelInfo.status == status)

        total = query.count()
        novels = query.offset((page - 1) * size).limit(size).all()

        items = [
            {
                'id': n.id,
                'novel_name': n.novel_name,
                'author_name': n.author_name,
                'category_name': n.category_name,
                'status': n.status,
                'word_count': n.word_count,
                'update_time': n.update_time,
                'intro': truncate_text(n.intro, 150) if n.intro else '',
                'source_url': n.source_url,
            }
            for n in novels
        ]

        return make_response(True, {
            'query': q,
            'page': page,
            'size': size,
            'total': total,
            'items': items
        }, 'OK')
    except Exception as e:
        logger.error(f"search_novels failed: {e}")
        return error_response(str(e))
    finally:
        db.close()


@novels_bp.route('/novels/<int:novel_id>', methods=['GET'])
def get_novel(novel_id):
    db = SessionLocal()
    try:
        novel = db.query(NovelInfo).filter(NovelInfo.id == novel_id).first()
        if not novel:
            return error_response('Novel not found', code=404)

        data = {
            'id': novel.id,
            'novel_name': novel.novel_name,
            'author_name': novel.author_name,
            'category_name': novel.category_name,
            'status': novel.status,
            'word_count': novel.word_count,
            'intro': novel.intro,
            'update_time': novel.update_time,
            'source_url': novel.source_url,
            'created_at': str(novel.created_at) if novel.created_at else None,
            'updated_at': str(novel.updated_at) if novel.updated_at else None,
        }
        return make_response(True, data, 'OK')
    except Exception as e:
        logger.error(f"get_novel failed: {e}")
        return error_response(str(e))
    finally:
        db.close()
