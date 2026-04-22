from flask import Blueprint, request
from models.db import SessionLocal, NovelInfo, TrendStat, KeywordStat
from sqlalchemy import func
from collections import defaultdict
from utils.response import make_response, error_response
from datetime import datetime, timedelta

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/keywords/global', methods=['GET'])
def keywords_global():
    db = SessionLocal()
    try:
        topk = int(request.args.get('topk', 50))
        source_field = request.args.get('source_field', None)
        q = db.query(
            KeywordStat.keyword.label('keyword'),
            func.sum(KeywordStat.weight).label('total_weight'),
            func.count(KeywordStat.novel_id).label('count'),
            KeywordStat.source_field.label('source_field')
        )
        if source_field:
            q = q.filter(KeywordStat.source_field == source_field)
        q = q.group_by(KeywordStat.keyword, KeywordStat.source_field)
        q = q.order_by(func.sum(KeywordStat.weight).desc()).limit(topk)
        rows = q.all()
        data = []
        for r in rows:
            data.append({
                'keyword': r.keyword,
                'total_weight': float(r.total_weight or 0),
                'count': int(r.count or 0),
                'source_field': r.source_field
            })
        return make_response(True, data, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/analysis/word-trend', methods=['GET'])
def analysis_word_trend():
    db = SessionLocal()
    try:
        granularity = request.args.get('granularity', 'day')
        days = int(request.args.get('days', 30))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = db.query(NovelInfo.update_time, NovelInfo.word_count).filter(
            NovelInfo.update_time != None
        )

        rows = query.all()

        def parse_dt(s):
            if not s:
                return None
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    return datetime.strptime(s, fmt)
                except Exception:
                    continue
            return None

        buckets = {}
        for upd, wcnt in rows:
            dt = parse_dt(upd)
            if dt is None:
                continue
            if granularity == 'week':
                start = dt - timedelta(days=dt.weekday())
                key = start.date()
            elif granularity == 'month':
                key = dt.strftime('%Y-%m')
            else:
                key = dt.date()
            buckets.setdefault(key, []).append(wcnt or 0)

        keys = sorted(buckets.keys())[-days:]
        dates = [str(k) for k in keys]
        avg_word_counts = []
        counts = []
        for k in keys:
            arr = buckets.get(k, [])
            c = len(arr)
            s = sum(arr)
            avg = (s / c) if c > 0 else 0
            avg_word_counts.append(avg)
            counts.append(c)
        return make_response(True, {'dates': dates, 'avg_word_counts': avg_word_counts, 'counts': counts}, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/analysis/category-trend', methods=['GET'])
def analysis_category_trend():
    db = SessionLocal()
    try:
        days = int(request.args.get('days', 30))
        top_categories = int(request.args.get('top_categories', 5))

        rows = db.query(NovelInfo.update_time, NovelInfo.category_name).filter(
            NovelInfo.update_time != None
        ).all()

        def parse_dt(s):
            if not s:
                return None
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    return datetime.strptime(s, fmt)
                except Exception:
                    continue
            return None

        date_cat_counts = {}
        total_by_cat = {}
        for upd, cat in rows:
            dt = parse_dt(upd)
            if dt is None:
                continue
            key = dt.date()
            if cat is None:
                cat = '未分类'
            date_cat_counts.setdefault((key, cat), 0)
            date_cat_counts[(key, cat)] += 1
            total_by_cat[cat] = total_by_cat.get(cat, 0) + 1

        top_cats = sorted(total_by_cat.items(), key=lambda x: x[1], reverse=True)[:top_categories]
        top_cat_names = [t[0] for t in top_cats]

        all_dates = sorted({d for (d, _) in date_cat_counts.keys()})
        last_dates = all_dates[-days:]
        dates = [str(d) for d in last_dates]

        series = []
        for c in top_cat_names:
            data = []
            for d in last_dates:
                data.append(date_cat_counts.get((d, c), 0))
            series.append({'name': c, 'data': data})

        return make_response(True, {'dates': dates, 'series': series}, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/analysis/category-distribution', methods=['GET'])
def category_distribution():
    db = SessionLocal()
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')

        query = db.query(
            NovelInfo.category_name,
            func.count(NovelInfo.id).label('count')
        )
        if category:
            query = query.filter(NovelInfo.category_name == category)
        if start_date:
            query = query.filter(NovelInfo.crawl_date >= start_date)
        if end_date:
            query = query.filter(NovelInfo.crawl_date <= end_date)

        rows = query.group_by(NovelInfo.category_name).all()

        total = sum(r.count for r in rows)
        raw = [(r.category_name or '未分类', r.count) for r in rows]
        raw.sort(key=lambda x: x[1], reverse=True)

        items = []
        for name, count in raw:
            items.append({
                'name': name,
                'count': count,
                'share': round(count / total, 4) if total > 0 else 0
            })

        return make_response(True, {
            'items': items,
            '_meta': {
                'total': total,
                'has_multi_batch': _has_multi_batch(db),
            }
        }, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/analysis/status-distribution', methods=['GET'])
def status_distribution():
    db = SessionLocal()
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = db.query(
            NovelInfo.status,
            func.count(NovelInfo.id).label('count')
        )
        if start_date:
            query = query.filter(NovelInfo.crawl_date >= start_date)
        if end_date:
            query = query.filter(NovelInfo.crawl_date <= end_date)

        rows = query.group_by(NovelInfo.status).all()

        total = sum(r.count for r in rows)
        items = []
        ongoing_count = 0
        finished_count = 0
        for r in rows:
            name = r.status or '未知'
            count = r.count
            share = round(count / total, 4) if total > 0 else 0
            items.append({'name': name, 'count': count, 'share': share})
            if '连载' in name:
                ongoing_count = count
            elif '完结' in name:
                finished_count = count

        items.sort(key=lambda x: x['count'], reverse=True)

        ratio = None
        if ongoing_count > 0 and finished_count > 0:
            ratio = round(ongoing_count / finished_count, 2)

        return make_response(True, {
            'items': items,
            'ongoing': {
                'count': ongoing_count,
                'share': round(ongoing_count / total, 4) if total > 0 else 0
            },
            'finished': {
                'count': finished_count,
                'share': round(finished_count / total, 4) if total > 0 else 0
            },
            'ratio': ratio,
            '_meta': {
                'total': total,
                'has_multi_batch': _has_multi_batch(db),
            }
        }, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/analysis/update-trend', methods=['GET'])
def update_trend():
    db = SessionLocal()
    try:
        days = int(request.args.get('days', 30))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        granularity = request.args.get('granularity', 'day')

        has_multi_batch = _has_multi_batch(db)

        if has_multi_batch:
            rows = db.query(NovelInfo.id, NovelInfo.crawl_date, NovelInfo.update_time).filter(
                NovelInfo.update_time != None,
                NovelInfo.crawl_date != None
            ).all()

            def parse_dt(s):
                if not s:
                    return None
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                    try:
                        return datetime.strptime(s, fmt)
                    except Exception:
                        continue
                return None

            crawl_buckets = {}
            all_novel_ids = set()
            for novel_id, crawl_dt, upd in rows:
                all_novel_ids.add(novel_id)
                cd = crawl_dt
                if isinstance(cd, datetime):
                    cd = cd.date()
                cd_str = str(cd)
                if start_date and cd_str < start_date:
                    continue
                if end_date and cd_str > end_date:
                    continue
                crawl_buckets.setdefault(cd_str, {'active_novels': set()})
                crawl_buckets[cd_str]['active_novels'].add(novel_id)

            total_novels = len(all_novel_ids)
            all_dates = sorted(crawl_buckets.keys())[-days:]
            dates = all_dates
            active_counts = []
            active_rates = []
            for d in all_dates:
                ac = len(crawl_buckets[d]['active_novels'])
                active_counts.append(ac)
                active_rates.append(round(ac / total_novels, 4) if total_novels > 0 else 0)

            return make_response(True, {
                'dates': dates,
                'active_counts': active_counts,
                'active_rates': active_rates,
                'has_multi_batch': True,
                'mode': 'multi_batch',
                '_meta': {
                    'total': total_novels,
                }
            }, 'OK')
        else:
            rows = db.query(NovelInfo.update_time).filter(
                NovelInfo.update_time != None
            ).all()

            def parse_dt(s):
                if not s:
                    return None
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                    try:
                        return datetime.strptime(s, fmt)
                    except Exception:
                        continue
                return None

            now = datetime.now()
            layers = {
                '今日': 0,
                '近3天': 0,
                '近7天': 0,
                '近30天': 0,
                '30天前': 0
            }

            for (upd,) in rows:
                dt = parse_dt(upd)
                if dt is None:
                    layers['30天前'] += 1
                    continue
                diff = (now - dt).days
                if diff < 1:
                    layers['今日'] += 1
                elif diff < 3:
                    layers['近3天'] += 1
                elif diff < 7:
                    layers['近7天'] += 1
                elif diff < 30:
                    layers['近30天'] += 1
                else:
                    layers['30天前'] += 1

            labels = list(layers.keys())
            counts = list(layers.values())
            total = sum(counts)

            return make_response(True, {
                'labels': labels,
                'counts': counts,
                'has_multi_batch': False,
                'mode': 'single_batch',
                '_meta': {
                    'total': total,
                }
            }, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/trends', methods=['GET'])
def trends():
    db = SessionLocal()
    try:
        dimension_type = request.args.get('dimension_type', '')
        days = int(request.args.get('days', 30))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        granularity = request.args.get('granularity', 'day')

        query = db.query(TrendStat)
        if dimension_type:
            query = query.filter(TrendStat.dimension_type == dimension_type)
        if start_date:
            query = query.filter(TrendStat.stat_date >= start_date)
        if end_date:
            query = query.filter(TrendStat.stat_date <= end_date)

        trends = query.order_by(TrendStat.stat_date.desc()).limit(days).all()

        data = [
            {
                'stat_date': str(t.stat_date),
                'dimension_type': t.dimension_type,
                'dimension_value': t.dimension_value,
                'novel_count': t.novel_count,
                'update_count': t.update_count,
                'avg_word_count': t.avg_word_count,
                'active_count': t.active_count,
                'share_value': t.share_value,
                'growth_rate': t.growth_rate,
                'trend_score': t.trend_score,
            }
            for t in trends
        ]

        return make_response(True, data, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/keywords', methods=['GET'])
def get_keywords():
    db = SessionLocal()
    try:
        from models.db import KeywordStat
        from sqlalchemy import func

        topk = int(request.args.get('topk', 100))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = db.query(
            KeywordStat.keyword,
            func.sum(KeywordStat.weight).label('total_weight'),
            func.count(KeywordStat.novel_id).label('keyword_freq')
        )

        if start_date or end_date:
            date_filter = []
            if start_date:
                date_filter.append(KeywordStat.created_at >= start_date)
            if end_date:
                date_filter.append(KeywordStat.created_at <= end_date)
            if date_filter:
                query = query.filter(*date_filter)

        keywords = query.group_by(
            KeywordStat.keyword
        ).order_by(
            func.sum(KeywordStat.weight).desc()
        ).limit(topk * 2).all()

        total_weight = 0
        result = {}
        for kw in keywords:
            word = kw.keyword
            if not word or len(word.strip()) < 2:
                continue
            if word.strip().isdigit() or word.replace('.', '', 1).replace('%', '', 1).isdigit():
                continue
            from utils.text_utils import is_noise_word, is_person_name
            if is_noise_word(word) or is_person_name(word):
                continue
            weight = float(kw.total_weight or 0)
            total_weight += weight
            result[word] = {
                'weight': weight,
                'keyword_freq': int(kw.keyword_freq or 0),
                'share_value': 0,
            }

        for word in result:
            result[word]['share_value'] = round(result[word]['weight'] / total_weight, 4) if total_weight > 0 else 0

        sorted_result = dict(sorted(result.items(), key=lambda x: x[1]['weight'], reverse=True)[:topk])

        return make_response(True, sorted_result, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/keywords/by-category', methods=['GET'])
def keywords_by_category():
    db = SessionLocal()
    try:
        from models.db import KeywordStat
        from sqlalchemy import func

        category = request.args.get('category', '')
        topk = int(request.args.get('topk', 50))

        query = db.query(
            KeywordStat.keyword,
            func.sum(KeywordStat.weight).label('total_weight')
        )

        if category:
            query = query.filter(KeywordStat.category_name == category)

        keywords = query.group_by(
            KeywordStat.keyword
        ).order_by(
            func.sum(KeywordStat.weight).desc()
        ).limit(topk).all()

        result = {kw.keyword: float(kw.total_weight or 0) for kw in keywords}
        return make_response(True, result, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


@analysis_bp.route('/analysis/genre-trend', methods=['GET'])
def genre_trend():
    db = SessionLocal()
    try:
        rows = db.query(
            NovelInfo.category_name,
            NovelInfo.crawl_date,
            NovelInfo.update_time,
            NovelInfo.id
        ).filter(
            NovelInfo.crawl_date != None
        ).all()

        def parse_dt(s):
            if not s:
                return None
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    return datetime.strptime(s, fmt)
                except Exception:
                    continue
            return None

        period_cat_count = {}
        period_cat_active = {}
        period_total = {}
        all_periods = set()
        all_cats = set()

        for cat, crawl_dt, upd, novel_id in rows:
            cat = cat or '未分类'
            cd = crawl_dt[:10] if crawl_dt and len(crawl_dt) >= 10 else crawl_dt
            all_periods.add(cd)
            all_cats.add(cat)
            period_cat_count.setdefault((cd, cat), 0)
            period_cat_count[(cd, cat)] += 1
            period_total.setdefault(cd, 0)
            period_total[cd] += 1
            dt = parse_dt(upd)
            if dt:
                diff = (datetime.now() - dt).days
                if diff <= 30:
                    period_cat_active.setdefault((cd, cat), 0)
                    period_cat_active[(cd, cat)] += 1

        periods = sorted(all_periods)
        categories = sorted(all_cats)

        category_trend = {}
        active_rate_trend = {}
        for cat in categories:
            category_trend[cat] = []
            active_rate_trend[cat] = []
            for p in periods:
                cnt = period_cat_count.get((p, cat), 0)
                category_trend[cat].append(cnt)
                active = period_cat_active.get((p, cat), 0)
                rate = round(active / cnt, 4) if cnt > 0 else 0
                active_rate_trend[cat].append(rate)

        top_cats_by_latest = sorted(
            categories,
            key=lambda c: category_trend[c][-1] if category_trend[c] else 0,
            reverse=True
        )[:8]

        trend_summary = {}
        for cat in top_cats_by_latest:
            data = category_trend[cat]
            if not data or all(v == 0 for v in data):
                continue
            first_nonzero = next((i for i, v in enumerate(data) if v > 0), 0)
            last_nonzero = len(data) - 1 - next((i for i, v in enumerate(reversed(data)) if v > 0), 0)
            duration = last_nonzero - first_nonzero + 1
            peak_idx = data.index(max(data))
            latest_val = data[-1]
            peak_val = max(data)
            if peak_val > 0 and latest_val > 0:
                trend_direction = 'rising' if latest_val >= peak_val * 0.9 else 'declining' if latest_val < peak_val * 0.5 else 'stable'
            else:
                trend_direction = 'inactive'
            latest_active = active_rate_trend[cat][-1] if active_rate_trend[cat] else 0
            trend_summary[cat] = {
                'duration_periods': duration,
                'first_period': periods[first_nonzero] if first_nonzero < len(periods) else '',
                'last_period': periods[last_nonzero] if last_nonzero < len(periods) else '',
                'peak_period': periods[peak_idx] if peak_idx < len(periods) else '',
                'peak_count': peak_val,
                'latest_count': latest_val,
                'trend_direction': trend_direction,
                'latest_active_rate': latest_active,
            }

        hot_periods = []
        for i, p in enumerate(periods):
            period_cats = sorted(
                [(c, category_trend[c][i]) for c in categories],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            hot_periods.append({
                'period': p,
                'top_categories': [{'name': c, 'count': v} for c, v in period_cats if v > 0],
                'total_novels': period_total.get(p, 0),
            })

        conclusion_parts = []
        if hot_periods:
            latest = hot_periods[-1]
            top_names = ', '.join([c['name'] for c in latest['top_categories']])
            conclusion_parts.append(
                f"最近一期（{latest['period']}）作者集中创作的题材为：{top_names}，"
                f"该期共采集 {latest['total_novels']} 部作品。"
            )
        rising_cats = [c for c, s in trend_summary.items() if s['trend_direction'] == 'rising']
        declining_cats = [c for c, s in trend_summary.items() if s['trend_direction'] == 'declining']
        if rising_cats:
            conclusion_parts.append(f"呈上升势头的题材：{', '.join(rising_cats)}，作者跟风创作热度仍在持续。")
        if declining_cats:
            conclusion_parts.append(f"呈减弱趋势的题材：{', '.join(declining_cats)}，作者创作热度正在消退。")
        long_cats = [c for c, s in trend_summary.items() if s['duration_periods'] >= len(periods) * 0.7]
        if long_cats:
            conclusion_parts.append(
                f"持续性较强的题材（覆盖超70%时间段）：{', '.join(long_cats)}，"
                f"说明此类题材具有稳定的创作基本盘。"
            )
        conclusion = ' '.join(conclusion_parts) if conclusion_parts else '数据不足，暂无法生成趋势结论。'

        return make_response(True, {
            'periods': periods,
            'categories': categories,
            'top_categories': top_cats_by_latest,
            'category_trend': {c: category_trend[c] for c in top_cats_by_latest},
            'active_rate_trend': {c: active_rate_trend[c] for c in top_cats_by_latest},
            'heatmap_data': [
                {'period': p, 'category': c, 'value': period_cat_count.get((p, c), 0)}
                for p in periods for c in categories
            ],
            'trend_summary': trend_summary,
            'hot_periods': hot_periods,
            'conclusion': conclusion,
            '_meta': {
                'total_periods': len(periods),
                'total_categories': len(categories),
                'has_multi_batch': _has_multi_batch(db),
            }
        }, 'OK')
    except Exception as e:
        return error_response(str(e))
    finally:
        db.close()


def _has_multi_batch(db):
    batches = db.query(NovelInfo.batch_no).filter(
        NovelInfo.batch_no != None
    ).distinct().all()
    return len([b for b in batches if b.batch_no]) > 1
