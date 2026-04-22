import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.keyword_service import process_keywords

result = process_keywords(method='tfidf', topk=20, batch_size=1000)
print(f'处理结果: {result}')
