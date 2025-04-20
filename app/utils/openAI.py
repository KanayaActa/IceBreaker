from decouple import config
from openai import OpenAI
import requests
import json

# 環境変数からキーとURLを取得
API_URL = config("API_URL")
client = OpenAI(api_key=config("OPENAI_API_KEY"))

# Function callingで使う関数定義
functions = [
    {
        "name": "get_category_ranking",
        "description": "指定されたカテゴリのランキングを取得します（最大10人）",
        "parameters": {
            "type": "object",
            "properties": {
                "category_name": {
                    "type": "string",
                    "description": "カテゴリ名（例: バスケットボール⛹️‍♀️、typing⌨️）"
                }
            },
            "required": ["category_name"]
        }
    },
    {
        "name": "search_users",
        "description": "名前やイントラ名でユーザーを検索します",
        "parameters": {
            "type": "object",
            "properties": {
                "search_key": {
                    "type": "string",
                    "description": "検索キーワード（部分一致）"
                }
            },
            "required": ["search_key"]
        }
    }
]

# カテゴリ名とIDのマッピング（固定ID）
CATEGORY_IDS = {
    "バスケットボール⛹️‍♀️": "6803cee775973e54f7023f84",
    "typing": "6803cf37bd1ca27affcb0089"
}

def call_get_category_ranking(category_name: str):
    category_id = CATEGORY_IDS.get(category_name)
    if not category_id:
        return f"不明なカテゴリ名です: {category_name}"

    try:
        response = requests.get(f"{API_URL}/api/ranking/category/{category_id}")
        response.raise_for_status()
        data = response.json()[:10]  # 最大10件に制限

        # ランキングを整形して返す
        return "\n".join([
            f"{item['rank']}位: {item['name']}（{item['rating']}）"
            for item in data
        ])
    except Exception as e:
        return f"API取得中にエラーが発生しました: {str(e)}"

def call_search_users(search_key: str):
    """
    ユーザー検索APIを呼び出す関数
    """
    try:
        # クエリパラメータとしてkeyを渡す
        params = {"key": search_key}
        response = requests.get(f"{API_URL}/api/user", params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return "該当するユーザーが見つかりませんでした。"
        
        # 検索結果を整形して返す
        result = "検索結果:\n"
        for i, user in enumerate(data, 1):
            name = user.get("name", "名前なし")
            intra_name = user.get("intra_name", "")
            
            
            result += f"{i}. {name} (intra@{intra_name})\n"
        
        return result
    except Exception as e:
        return f"ユーザー検索中にエラーが発生しました: {str(e)}"

def openai_api(content: str) -> str:
    """
    OpenAI function calling を使ってカテゴリ名からランキングを取得またはユーザー検索を実行。
    """
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": "あなたはスポーツやスキルカテゴリのランキングを取得したり、ユーザー検索ができるアシスタントです。"
            },
            {
                "role": "user",
                "content": content
            }
        ],
        functions=functions,
        function_call="auto"
    )

    choice = chat_response.choices[0]

    # Function Call がトリガーされた場合
    if choice.finish_reason == "function_call":
        func_name = choice.message.function_call.name
        arguments = choice.message.function_call.arguments

        if func_name == "get_category_ranking":
            args = json.loads(arguments)
            category_name = args.get("category_name")
            return call_get_category_ranking(category_name)
        
        elif func_name == "search_users":
            args = json.loads(arguments)
            search_key = args.get("search_key")
            return call_search_users(search_key)

    # 通常のテキスト応答があった場合
    return choice.message.content or "応答がありませんでした。"