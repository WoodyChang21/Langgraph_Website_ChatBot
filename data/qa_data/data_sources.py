"""
URL configuration dictionary for website crawling.
Each entry contains the source name and URL for FireCrawl processing.
"""

URLS_CONFIG = {
    "品牌故事": "https://www.countess.tw/v2/Official/BrandStory",
    "商店簡介": "https://www.countess.tw/shop/introduce/1876?t=1",
    "寢具知識_幼兒園午睡寢具_Q&A": "https://www.countess.tw/page/childrens_bedding",
    "寢具知識_宿舍寢具怎麼選": "https://www.countess.tw/page/ichin_school",
    "寢具知識_CPS頸肩量測選枕": "https://www.countess.tw/Article/Detail/31125",
    "企業報導_ESG永續經營理念": "https://www.countess.tw/page/ichin-ESG",
    "寢具知識_寢具如何洗滌保養": "https://www.countess.tw/Article/Detail/46825",
    "寢具知識_如何挑選合適棉被及收納保養": "https://www.countess.tw/Article/Detail/33436",
}

# Alternative format: List of dictionaries (more structured)
URLS_LIST = [
    {
        "source": "品牌故事",
        "url": "https://www.countess.tw/v2/Official/BrandStory",
        "category": "品牌資訊"
    },
    {
        "source": "商店簡介",
        "url": "https://www.countess.tw/shop/introduce/1876?t=1",
        "category": "商店資訊"
    },
    {
        "source": "寢具知識_幼兒園午睡寢具_Q&A",
        "url": "https://www.countess.tw/page/childrens_bedding",
        "category": "寢具知識"
    },
    {
        "source": "寢具知識_宿舍寢具怎麼選",
        "url": "https://www.countess.tw/page/ichin_school",
        "category": "寢具知識"
    },
    {
        "source": "寢具知識_CPS頸肩量測選枕",
        "url": "https://www.countess.tw/Article/Detail/31125",
        "category": "寢具知識"
    },
    {
        "source": "企業報導_ESG永續經營理念",
        "url": "https://www.countess.tw/page/ichin-ESG",
        "category": "企業報導"
    },
    {
        "source": "寢具知識_寢具如何洗滌保養",
        "url": "https://www.countess.tw/Article/Detail/46825",
        "category": "寢具知識"
    },
    {
        "source": "寢具知識_如何挑選合適棉被及收納保養",
        "url": "https://www.countess.tw/Article/Detail/33436",
        "category": "寢具知識"
    },
]

# Simple list format (just URLs)
URLS_SIMPLE = [
    "https://www.countess.tw/v2/Official/BrandStory",
    "https://www.countess.tw/shop/introduce/1876?t=1",
    "https://www.countess.tw/page/childrens_bedding",
    "https://www.countess.tw/page/ichin_school",
    "https://www.countess.tw/Article/Detail/31125",
    "https://www.countess.tw/page/ichin-ESG",
    "https://www.countess.tw/Article/Detail/46825",
    "https://www.countess.tw/Article/Detail/33436",
]

