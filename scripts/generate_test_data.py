"""
生成本地测试数据用于可视化展示
包含多批次小说数据、关键词统计、趋势统计等
"""
import sys
import os
import random
import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db import SessionLocal, PlatformSource, NovelRaw, NovelInfo, KeywordStat, TrendStat, init_db
from utils.logger import get_logger

logger = get_logger(__name__)

NOVEL_NAMES = [
    "斗破苍穹", "武动乾坤", "大主宰", "元尊", "圣墟", "完美世界", "遮天", "凡人修仙传",
    "仙逆", "求魔", "我欲封天", "一念永恒", "三寸人间", "太古神王", "星辰变", "盘龙",
    "九星霸体诀", "全职法师", "神印王座", "斗罗大陆", "绝世唐门", "龙王传说", "终极斗罗",
    "神墓", "长生界", "不死不灭", "邪神传说", "佣兵天下", "紫川", "英雄志",
    "雪中悍刀行", "剑来", "大道朝天", "择天记", "将夜", "庆余年", "赘婿", "夜天子",
    "明朝那些事儿", "回到明朝当王爷", "官道之色戒", "医道龙神", "都市极品医神", "最强狂兵",
    "天才医生", "透视之眼", "超级兵王", "特种教师", "最强弃少", "校花的贴身高手",
    "吞噬星空", "莽荒纪", "纪宁传", "宇宙职业选手", "深空彼岸", "夜的命名术",
    "诡秘之主", "宿命之环", "惊悚乐园", "轮回乐园", "超神机械师", "全职高手",
    "蝴蝶效应", "时间之墟", "死亡万花筒", "我有一座冒险屋", "恐怖复苏", "深夜书屋",
    "游戏纪元", "重生之贼行天下", "网游之纵横天下", "英雄联盟之王者归来",
    "历史之舟", "大明文魁", "唐砖", "秦吏", "汉乡", "宋时明月", "清穿之四爷宠妃",
    "科学修仙指南", "我在末世有套房", "黑科技垄断公司", "重生之神级学霸", "天才基本法",
    "我的云养女友", "我真没想重生啊", "俗人回档", "老衲还年轻", "最好的我们", "你好旧时光",
    "逆天邪神", "万族之劫", "第一序列", "全球高武", "修真聊天群", "大王饶命",
    "牧神记", "临渊行", "伏天氏", "万古神帝", "太初", "三界独尊",
    "龙符", "儒道至圣", "造化之门", "最强反套路系统", "我师兄实在太稳健了", "从红月开始",
    "大奉打更人", "赤心巡天", "星门", "明克街13号", "这个人仙太过正经", "长夜余火",
    "深海余烬", "灵境行者", "不科学御兽", "我的徒弟都是大反派", "开局签到荒古圣体",
    "我的治愈系游戏", "这游戏也太真实了", "我在斩妖司除魔三十年", "大魏读书人", "我只是个凡人",
    "全球轮回：只有我知道剧情", "我的模拟长生路", "道诡异仙", "光阴之外",
    "仙工开物", "谁让他修仙的", "玄鉴仙族", "我的模拟乐园", "修仙就是这样子的",
    "我真没想当反派啊", "从赘婿到宠臣", "万相之王", "夜无疆", "环命运",
    "十日终焉", "玩家凶猛", "我加载了怪谈游戏", "我不是戏神", "赛博英雄传",
    "走进修仙", "走进不科学", "走进赛博朋克", "走进魔法世界", "走进修仙世界",
    "走进武侠世界", "走进仙侠世界", "走进玄幻世界", "走进科幻世界", "走进游戏世界",
    "走进历史世界", "走进都市世界", "走进灵异世界", "走进奇幻世界", "走进轻小说世界",
    "我的修仙模拟器", "我的武侠模拟器", "我的仙侠模拟器", "我的玄幻模拟器", "我的科幻模拟器",
    "我的游戏模拟器", "我的历史模拟器", "我的都市模拟器", "我的灵异模拟器", "我的奇幻模拟器",
    "我的轻小说模拟器", "我的修仙人生", "我的武侠人生", "我的仙侠人生", "我的玄幻人生",
    "我的科幻人生", "我的人生模拟器", "我的游戏人生", "我的历史人生", "我的都市人生",
    "我的灵异人生", "我的奇幻人生", "我的轻小说人生", "我的修仙日记", "我的武侠日记",
    "我的仙侠日记", "我的玄幻日记", "我的科幻日记", "我的游戏日记", "我的历史日记",
    "我的都市日记", "我的灵异日记", "我的奇幻日记", "我的轻小说日记", "我的修仙笔记",
    "我的武侠笔记", "我的仙侠笔记", "我的玄幻笔记", "我的科幻笔记", "我的游戏笔记",
    "我的历史笔记", "我的都市笔记", "我的灵异笔记", "我的奇幻笔记", "我的轻小说笔记",
    "我的修仙手札", "我的武侠手札", "我的仙侠手札", "我的玄幻手札", "我的科幻手札",
    "我的游戏手札", "我的手札", "我的都市手札", "我的灵异手札", "我的奇幻手札",
    "我的轻小说手札", "我的修仙录", "我的武侠录", "我的仙侠录", "我的玄幻录",
    "我的科幻录", "我的游戏录", "我的历史录", "我的都市录", "我的灵异录",
    "我的奇幻录", "我的轻小说录", "我的修仙传", "我的武侠传", "我的仙侠传",
    "我的玄幻传", "我的科幻传", "我的游戏传", "我的历史传", "我的都市传",
    "我的灵异传", "我的奇幻传", "我的轻小说传", "我的修仙记", "我的武侠记"
]

AUTHOR_NAMES = [
    "天蚕土豆", "辰东", "耳根", "我吃西红柿", "唐家三少", "梦入神机", "猫腻", "烽火戏诸侯",
    "月关", "愤怒的香蕉", "厌笔萧生", "忘语", "萧鼎", "天下霸唱", "南派三叔", "蝴蝶蓝",
    "爱潜水的乌贼", "会说话的肘子", "黑山老鬼", "卖报小郎君", "远瞳", "齐佩甲", "熊狼狗",
    "三天两觉", "风凌天下", "打眼", "柳下挥", "鱼人二代", "狂笑", "七十二编",
    "特别能能", "知白", "孑与2", "希行", "吱吱", "丁墨", "priest", "墨香铜臭"
]

CATEGORIES = [
    "玄幻奇幻", "都市言情", "武侠仙侠", "科幻末世", "历史军事", "游戏竞技",
    "悬疑灵异", "轻小说", "奇幻", "仙侠", "都市", "玄幻", "科幻", "历史", "游戏"
]

STATUSES = ["连载中", "已完结"]

KEYWORDS = [
    "系统", "重生", "穿越", "修仙", "热血", "爽文", "逆袭", "扮猪吃虎",
    "无敌流", "后宫", "单女主", "多女主", "无女主", "搞笑", "轻松", "暗黑",
    "杀伐果断", "智商在线", "慢热", "快节奏", "群像", "种田", "争霸", "探险",
    "末世", "灵气复苏", "洪荒", "封神", "西游", "三国", "武侠", "江湖",
    "剑道", "丹道", "阵法", "炼器", "御兽", "召唤", "机甲", "魔法", "斗气",
    "武魂", "血脉", "天赋", "功法", "法宝", "丹药", "秘境", "遗迹", "古墓"
]


def generate_platforms(db):
    platforms = [
        {"platform_name": "起点中文网", "platform_url": "https://www.qidian.com", "remark": "阅文集团旗下"},
        {"platform_name": "纵横中文网", "platform_url": "https://www.zongheng.com", "remark": "百度文学"},
        {"platform_name": "17K小说网", "platform_url": "https://www.17k.com", "remark": "中文在线"},
        {"platform_name": "番茄小说", "platform_url": "https://www.fanqienovel.com", "remark": "字节跳动"},
        {"platform_name": "七猫小说", "platform_url": "https://www.qimao.com", "remark": "七猫免费小说"},
    ]
    
    created = []
    for p in platforms:
        existing = db.query(PlatformSource).filter(PlatformSource.platform_name == p["platform_name"]).first()
        if not existing:
            platform = PlatformSource(**p)
            db.add(platform)
            db.flush()
            created.append(platform)
        else:
            created.append(existing)
    
    db.flush()
    logger.info(f"Created {len(created)} platforms")
    return created


def generate_novel_batches(db, platforms, num_batches=5, novels_per_batch=30):
    base_date = datetime.datetime.now()
    
    for batch_idx in range(num_batches):
        batch_date = base_date - datetime.timedelta(days=(num_batches - batch_idx - 1) * 7)
        batch_no = f"batch_{batch_date.strftime('%Y%m%d')}"
        
        logger.info(f"Generating batch {batch_no} with {novels_per_batch} novels")
        
        selected_names = random.sample(NOVEL_NAMES, min(novels_per_batch, len(NOVEL_NAMES)))
        
        for i, name in enumerate(selected_names):
            platform = random.choice(platforms)
            author = random.choice(AUTHOR_NAMES)
            category = random.choice(CATEGORIES)
            status = random.choice(STATUSES) if batch_idx < num_batches - 1 else random.choices(STATUSES, weights=[0.7, 0.3])[0]
            
            word_count = random.randint(100000, 5000000)
            
            update_days_offset = random.randint(-30, 0)
            update_time = batch_date + datetime.timedelta(days=update_days_offset)
            update_time_str = update_time.strftime("%Y-%m-%d %H:%M:%S")
            
            existing = db.query(NovelInfo).filter(
                NovelInfo.novel_name == name,
                NovelInfo.author_name == author,
                NovelInfo.platform_id == platform.id
            ).first()
            
            source_url = f"https://example.com/{platform.platform_name}/{name}"
            
            existing_by_url = db.query(NovelInfo).filter(
                NovelInfo.source_url == source_url
            ).first()
            
            if not existing and not existing_by_url:
                raw = NovelRaw(
                    platform_id=platform.id,
                    batch_no=batch_no,
                    source_url=source_url,
                    novel_name_raw=name,
                    author_name_raw=author,
                    category_name_raw=category,
                    status_raw=status,
                    word_count_raw=word_count,
                    intro_raw=f"这是一部{category}小说，讲述了精彩的故事。",
                    update_time_raw=update_time_str,
                    crawl_time=batch_date
                )
                db.add(raw)
                db.flush()
                
                info = NovelInfo(
                    raw_id=raw.id,
                    platform_id=platform.id,
                    novel_name=name,
                    author_name=author,
                    category_name=category,
                    status=status,
                    word_count=word_count,
                    intro=f"这是一部{category}小说，讲述了精彩的故事。",
                    update_time=update_time_str,
                    source_url=source_url,
                    crawl_date=batch_date.strftime("%Y-%m-%d"),
                    batch_no=batch_no,
                    created_at=batch_date,
                    updated_at=batch_date
                )
                db.add(info)
            else:
                target = existing if existing else existing_by_url
                target.word_count = word_count
                target.update_time = update_time_str
                target.crawl_date = batch_date.strftime("%Y-%m-%d")
                target.batch_no = batch_no
                target.updated_at = batch_date
        
        db.flush()
        logger.info(f"Batch {batch_no} generated")


def generate_keywords(db):
    novels = db.query(NovelInfo).all()
    
    for novel in novels:
        num_keywords = random.randint(3, 8)
        selected_keywords = random.sample(KEYWORDS, min(num_keywords, len(KEYWORDS)))
        
        for keyword in selected_keywords:
            existing = db.query(KeywordStat).filter(
                KeywordStat.novel_id == novel.id,
                KeywordStat.keyword == keyword
            ).first()
            
            if not existing:
                weight = random.uniform(0.1, 1.0)
                source_field = random.choice(["title", "intro", "category", "tags"])
                
                kw_stat = KeywordStat(
                    novel_id=novel.id,
                    category_name=novel.category_name,
                    keyword=keyword,
                    weight=weight,
                    source_field=source_field
                )
                db.add(kw_stat)
    
    db.flush()
    logger.info(f"Keywords generated for {len(novels)} novels")


def generate_trend_stats(db):
    novels = db.query(NovelInfo).all()
    
    if not novels:
        return
    
    batches = defaultdict(list)
    for novel in novels:
        if novel.batch_no and novel.crawl_date:
            batches[novel.crawl_date].append(novel)
    
    sorted_dates = sorted(batches.keys())
    
    for stat_date in sorted_dates:
        batch_novels = batches[stat_date]
        
        cat_stats = defaultdict(lambda: {"count": 0, "total_words": 0})
        for novel in batch_novels:
            cat = novel.category_name or "未知"
            cat_stats[cat]["count"] += 1
            if novel.word_count:
                cat_stats[cat]["total_words"] += novel.word_count
        
        total_novels = len(batch_novels)
        for cat, stats in cat_stats.items():
            existing = db.query(TrendStat).filter(
                TrendStat.stat_date == stat_date,
                TrendStat.dimension_type == "category",
                TrendStat.dimension_value == cat
            ).first()
            
            avg_words = stats["total_words"] / stats["count"] if stats["count"] > 0 else 0
            share = stats["count"] / total_novels if total_novels > 0 else 0
            
            if not existing:
                trend = TrendStat(
                    stat_date=stat_date,
                    dimension_type="category",
                    dimension_value=cat,
                    novel_count=stats["count"],
                    update_count=stats["count"],
                    avg_word_count=avg_words,
                    active_count=stats["count"],
                    share_value=share,
                    growth_rate=None,
                    trend_score=share * 100
                )
                db.add(trend)
        
        status_stats = defaultdict(lambda: {"count": 0, "total_words": 0})
        for novel in batch_novels:
            status = novel.status or "未知"
            status_stats[status]["count"] += 1
            if novel.word_count:
                status_stats[status]["total_words"] += novel.word_count
        
        for status, stats in status_stats.items():
            existing = db.query(TrendStat).filter(
                TrendStat.stat_date == stat_date,
                TrendStat.dimension_type == "status",
                TrendStat.dimension_value == status
            ).first()
            
            avg_words = stats["total_words"] / stats["count"] if stats["count"] > 0 else 0
            share = stats["count"] / total_novels if total_novels > 0 else 0
            
            if not existing:
                trend = TrendStat(
                    stat_date=stat_date,
                    dimension_type="status",
                    dimension_value=status,
                    novel_count=stats["count"],
                    update_count=stats["count"],
                    avg_word_count=avg_words,
                    active_count=stats["count"],
                    share_value=share,
                    growth_rate=None,
                    trend_score=share * 100
                )
                db.add(trend)
    
    if len(sorted_dates) >= 2:
        for i in range(1, len(sorted_dates)):
            prev_date = sorted_dates[i-1]
            curr_date = sorted_dates[i]
            
            prev_cats = db.query(TrendStat).filter(
                TrendStat.stat_date == prev_date,
                TrendStat.dimension_type == "category"
            ).all()
            
            curr_cats = db.query(TrendStat).filter(
                TrendStat.stat_date == curr_date,
                TrendStat.dimension_type == "category"
            ).all()
            
            prev_cat_map = {t.dimension_value: t.novel_count for t in prev_cats}
            
            for curr_trend in curr_cats:
                prev_count = prev_cat_map.get(curr_trend.dimension_value)
                if prev_count and prev_count > 0:
                    growth_rate = (curr_trend.novel_count - prev_count) / prev_count
                    curr_trend.growth_rate = growth_rate
    
    db.flush()
    logger.info(f"Trend stats generated for {len(sorted_dates)} batches")


def main():
    logger.info("Starting to generate test data...")
    
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        return
    
    db = SessionLocal()
    
    try:
        logger.info("Step 1: Generating platforms...")
        platforms = generate_platforms(db)
        db.commit()
        
        logger.info("Step 2: Generating novel batches...")
        generate_novel_batches(db, platforms, num_batches=5, novels_per_batch=80)
        db.commit()
        
        logger.info("Step 3: Generating keywords...")
        generate_keywords(db)
        db.commit()
        
        logger.info("Step 4: Generating trend stats...")
        generate_trend_stats(db)
        db.commit()
        
        total_novels = db.query(NovelInfo).count()
        total_keywords = db.query(KeywordStat).count()
        total_trends = db.query(TrendStat).count()
        total_batches = db.query(NovelInfo.batch_no).filter(NovelInfo.batch_no != None).distinct().count()
        
        logger.info("=" * 50)
        logger.info("Test data generation completed!")
        logger.info(f"Total novels: {total_novels}")
        logger.info(f"Total batches: {total_batches}")
        logger.info(f"Total keywords: {total_keywords}")
        logger.info(f"Total trend records: {total_trends}")
        logger.info("=" * 50)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating test data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
