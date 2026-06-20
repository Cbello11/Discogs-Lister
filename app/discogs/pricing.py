from datetime import datetime, timedelta
from app.database import db
from app.models import PriceCache
from app.discogs.client import get_client


def get_price_suggestions(release_id):
    release_id = int(release_id)
    cache = PriceCache.query.filter_by(release_id=release_id).first()
    ttl = timedelta(hours=1)

    if cache and (datetime.utcnow() - cache.cached_at) < ttl:
        return _format_cache(cache)

    try:
        d = get_client()
        stats = d.release(release_id).marketplace_stats
        low = float(stats.lowest_price.value) if stats.lowest_price else None
        median = float(stats.median_price.value) if stats.median_price else None
        high = float(stats.highest_price.value) if stats.highest_price else None
        num = int(stats.num_for_sale) if stats.num_for_sale else 0
    except Exception:
        return {"low": None, "median": None, "high": None, "num_for_sale": 0, "suggested": None}

    if cache:
        cache.low_price = low
        cache.median_price = median
        cache.high_price = high
        cache.num_for_sale = num
        cache.cached_at = datetime.utcnow()
    else:
        cache = PriceCache(
            release_id=release_id,
            low_price=low,
            median_price=median,
            high_price=high,
            num_for_sale=num,
        )
        db.session.add(cache)
    db.session.commit()

    return _format_cache(cache)


def _format_cache(cache):
    suggested = None
    if cache.median_price:
        suggested = round(cache.median_price * 2) / 2  # round to nearest $0.50
    return {
        "low": cache.low_price,
        "median": cache.median_price,
        "high": cache.high_price,
        "num_for_sale": cache.num_for_sale,
        "suggested": suggested,
    }
