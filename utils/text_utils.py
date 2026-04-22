import re


def clean_html_tags(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def clean_special_chars(text):
    if not text:
        return ''
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
    return text.strip()


def normalize_whitespace(text):
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_word_count(text):
    if not text:
        return None
    text = str(text).strip()
    text = text.replace(',', '').replace('，', '')
    match = re.search(r'(\d+)', text)
    if match:
        try:
            return int(match.group(1))
        except:
            pass
    return None


def truncate_text(text, max_length=200):
    if not text:
        return ''
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'


STOPWORDS = {
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
    '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '里', '为', '什么', '她', '他', '它们', '吧', '啊',
    '吗', '呢', '嘛', '哦', '呀', '呃', '嗯', '唉', '喂', '嘿', '哈', '哎', '诶', '噢', '哟',
    '的', '之', '与', '或', '而', '且', '但', '若', '则', '因', '所以', '但是', '然后', '于是', '接着',
    '这个', '那个', '那些', '这些', '这样', '那样', '怎么', '如何', '为什么', '多少',
}

NOISE_WORDS = {
    '有端', '张楚', '张楚岚', '楚岚', '冯宝宝', '宝宝', '王也', '诸葛', '诸葛青',
    '萧炎', '唐三', '林动', '牧尘', '周元', '叶凡', '石昊', '叶凡', '楚风',
    '李七夜', '纪宁', '罗峰', '孟浩', '白小纯', '韩立', '王林', '苏铭',
    '秦羽', '辰东', '土豆', '天蚕', '耳根', '辰东', '烽火', '猫腻',
    '唐家', '三少', '我吃', '西红柿', '天蚕土豆', '爱潜水的', '乌贼',
    '起点', '中文网', '晋江', '纵横', '17K', '17k', 'k小说网', '小说网',
    '微信', '公众号', '关注', '订阅', '收藏', '推荐', '阅读', '免费',
    '更新', '章节', '正文', '目录', '简介', '简介:', '简介：',
    'QQ', 'qq', '群', '书友群', '读者群', '交流群', '加群', '扣扣',
    '作者', '新书', '完本', '连载', '完本小说', '全本小说',
    '第一章', '第二章', '第三章', '第四章', '第五章',
    '第01章', '第02章', '第03章',
    '卷一', '卷二', '卷三', '卷四', '卷五',
    '上部', '中部', '下部', '前传', '后传', '外传',
    '同名', '改编', '漫画', '动画', '影视', '游戏', '小说',
    '都市', '玄幻', '仙侠', '历史', '军事', '游戏', '科幻', '悬疑',
    '穿越', '重生', '系统', '无敌', '最强', '巅峰', '至尊', '大帝',
    '神王', '战神', '剑神', '丹神', '阵神', '符神', '器神',
    '都市', '热血', '爽文', '后宫', '种马', 'YY', 'yy',
    '本书', '本文', '本书籍', '本书已', '本书将', '本书讲述',
    '故事', '讲述', '描述', '描写', '刻画', '展现', '呈现',
    '世界', '大陆', '星球', '宇宙', '时空', '异界', '异世界',
    '主角', '男主', '女主', '主人公', '男主角', '女主角',
    '一个', '一些', '一切', '一切', '一切',
    '如果', '如果', '如果', '如果', '如果',
}

COMMON_SURNAMES = {
    '张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴',
    '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
    '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
    '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕',
    '苏', '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎',
    '余', '潘', '杜', '戴', '夏', '钟', '汪', '田', '任', '姜',
    '范', '方', '石', '姚', '谭', '廖', '邹', '熊', '金', '陆',
    '郝', '孔', '白', '崔', '康', '毛', '邱', '秦', '江', '史',
    '顾', '侯', '邵', '孟', '龙', '万', '段', '雷', '钱', '汤',
    '尹', '黎', '易', '常', '武', '乔', '贺', '赖', '龚', '文',
    '庞', '樊', '兰', '殷', '施', '陶', '翟', '安', '颜', '倪',
    '严', '牛', '温', '芦', '季', '俞', '章', '鲁', '葛', '伍',
    '韦', '申', '尤', '毕', '聂', '丛', '焦', '向', '柳', '邢',
    '路', '岳', '齐', '沿', '梅', '莫', '庄', '辛', '管', '祝',
    '左', '涂', '谷', '祁', '时', '舒', '耿', '牟', '卜', '路',
    '詹', '关', '苗', '凌', '费', '纪', '靳', '盛', '童', '欧',
    '甄', '项', '曲', '成', '游', '阳', '裴', '席', '卫', '查',
    '屈', '鲍', '位', '覃', '霍', '翁', '隋', '植', '甘', '景',
    '薄', '单', '包', '司', '柏', '宁', '柯', '阮', '桂', '闵',
    '欧阳', '解', '强', '柴', '华', '车', '冉', '房', '边', '辜',
}


def is_stopword(word):
    return word in STOPWORDS or len(word) < 2


def is_noise_word(word):
    return word in NOISE_WORDS


def is_person_name(word):
    if len(word) < 2 or len(word) > 4:
        return False
    surname = word[0]
    if word[:2] in COMMON_SURNAMES:
        surname = word[:2]
    elif surname not in COMMON_SURNAMES:
        return False
    rest = word[len(surname):]
    if not rest:
        return False
    name_indicators = {'楚', '岚', '宝', '也', '青', '炎', '三', '动', '尘', '元', '凡', '昊', '风',
                       '七', '夜', '宁', '峰', '浩', '纯', '立', '林', '铭', '羽', '东', '豆', '蚕',
                       '根', '火', '贼', '腻', '乌', '贼', '少', '茄', '潜', '水', '家'}
    if any(c in name_indicators for c in rest):
        return True
    if len(rest) <= 2:
        return False
    return False


def is_valid_keyword(word):
    if is_stopword(word):
        return False
    if is_noise_word(word):
        return False
    if word.isdigit() or word.replace('.', '', 1).replace('%', '', 1).isdigit():
        return False
    if len(word) < 2:
        return False
    if is_person_name(word):
        return False
    if re.match(r'^[a-zA-Z]{1,2}$', word):
        return False
    return True