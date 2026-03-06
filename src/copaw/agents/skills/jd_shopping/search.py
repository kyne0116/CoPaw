# -*- coding: utf-8 -*-
"""京东商品搜索和比价功能"""
import re
from typing import Any


def search_and_compare(keyword: str, max_results: int = 5) -> dict[str, Any]:
    """
    在京东搜索商品并比价推荐

    Args:
        keyword: 商品关键词
        max_results: 最多比较的商品数量

    Returns:
        包含搜索结果和推荐的字典
    """
    from copaw.agents.tools.browser_control import browser_use

    results = []

    # 启动浏览器并打开京东
    browser_use(action="start", headless=False)
    browser_use(action="navigate", url="https://www.jd.com")

    # 搜索商品
    browser_use(action="snapshot", interactive=True)
    browser_use(action="type", ref="e1", text=keyword)
    browser_use(action="click", ref="e2")
    browser_use(action="wait_for", selector=".gl-item", timeout=5000)

    # 提取商品信息
    script = """
    Array.from(document.querySelectorAll('.gl-item')).slice(0, %d).map(item => ({
        title: item.querySelector('.p-name em')?.textContent.trim(),
        price: item.querySelector('.p-price i')?.textContent.trim(),
        shop: item.querySelector('.p-shop')?.textContent.trim(),
        link: item.querySelector('.p-img a')?.href
    }))
    """ % max_results

    response = browser_use(action="evaluate", expression=script)
    products = response.get("result", [])

    # 分析推荐
    best = None
    if products:
        valid = [p for p in products if p.get("price")]
        if valid:
            best = min(valid, key=lambda x: float(re.sub(r"[^\d.]", "", x["price"])))

    browser_use(action="stop")

    return {
        "keyword": keyword,
        "products": products,
        "recommendation": best,
        "total": len(products)
    }
