from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.database.connection import ratings_collection
from app.schemas.rating import RatingCreate, RatingInDB

from collections import defaultdict


async def create_rating(rating: RatingCreate) -> RatingInDB:
    """
    Create a new rating in the database (履歴として追加).
    """
    rating_dict = rating.model_dump()
    rating_dict["created_at"] = datetime.utcnow()
    rating_dict["updated_at"] = datetime.utcnow()

    # Convert string IDs to ObjectId for storage
    rating_dict["user_id"] = ObjectId(rating_dict["user_id"])
    rating_dict["category_id"] = ObjectId(rating_dict["category_id"])

    result = await ratings_collection.insert_one(rating_dict)
    created_rating = await ratings_collection.find_one({"_id": result.inserted_id})

    # Convert ObjectId back to string for response
    created_rating["_id"] = str(created_rating["_id"])
    created_rating["user_id"] = str(created_rating["user_id"])
    created_rating["category_id"] = str(created_rating["category_id"])

    return RatingInDB(**created_rating)


async def get_rating(rating_id: str) -> Optional[RatingInDB]:
    """
    Get a rating by ID.
    """
    try:
        rating = await ratings_collection.find_one({"_id": ObjectId(rating_id)})
        if rating:
            rating["_id"] = str(rating["_id"])
            rating["user_id"] = str(rating["user_id"])
            rating["category_id"] = str(rating["category_id"])
            return RatingInDB(**rating)
    except Exception:
        return None
    return None


async def get_user_category_rating(user_id: str, category_id: str) -> Optional[RatingInDB]:
    """
    Get the latest rating for a user and category.
    """
    try:
        rating = await ratings_collection.find_one(
            {
                "user_id": ObjectId(user_id),
                "category_id": ObjectId(category_id)
            },
            sort=[("date", -1)]  # 最新のレーティングを取得
        )
        if rating:
            rating["_id"] = str(rating["_id"])
            rating["user_id"] = str(rating["user_id"])
            rating["category_id"] = str(rating["category_id"])
            return RatingInDB(**rating)
    except Exception:
        return None
    return None


async def get_user_rating_history(user_id: str, category_id: str) -> List[RatingInDB]:
    """
    Get full rating history for a user in a category.
    """
    try:
        cursor = ratings_collection.find({
            "user_id": ObjectId(user_id),
            "category_id": ObjectId(category_id)
        }).sort("date", 1)

        ratings = []
        async for rating in cursor:
            rating["_id"] = str(rating["_id"])
            rating["user_id"] = str(rating["user_id"])
            rating["category_id"] = str(rating["category_id"])
            ratings.append(RatingInDB(**rating))

        return ratings
    except Exception:
        return []




async def get_category_rankings(category_id: str) -> List[RatingInDB]:
    """
    Get latest ratings for a category, sorted by rate descending, with duplicates (by user) removed.
    """
    try:
        cursor = ratings_collection.find(
            {"category_id": ObjectId(category_id)}
        ).sort("rate", -1)

        # ユーザーごとの最新評価を格納するための辞書
        user_ratings = defaultdict(lambda: None)
        
        async for rating in cursor:
            user_id = str(rating["user_id"])
            # 最新の評価のみを保持
            if user_ratings[user_id] is None or rating["rate"] > user_ratings[user_id]["rate"]:
                rating["_id"] = str(rating["_id"])
                rating["user_id"] = user_id
                rating["category_id"] = str(rating["category_id"])
                user_ratings[user_id] = rating
        
        # 辞書に格納された評価をリストに変換
        ratings = [RatingInDB(**rating) for rating in user_ratings.values()]
        
        # レートで降順にソート
        ratings.sort(key=lambda r: r.rate, reverse=True)

        return ratings
    except Exception:
        return []
