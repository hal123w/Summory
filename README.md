# Summory

長文を貼ると AI（Gemini）が要約し、履歴として残してあとで見返せるアプリ（Django）。

## 機能（MVP）

- ログイン・新規登録・ログアウト
- **トップ（`/`）で原文を貼って要約・保存**（原文も保存）
- 履歴一覧は `/history/`（要約が主役）／詳細（原文は折りたたみ）
- カテゴリ（任意・1つ）。「すべて」とカテゴリ別一覧
- 編集・削除

## ローカルセットアップ

```powershell
cd summory
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`.env.example` をコピーして `.env` を作成します。

```powershell
Copy-Item .env.example .env
```

### Gemini API キーの置き方

1. [Google AI Studio](https://aistudio.google.com/apikey) で API キーを作成
2. `.env` に次を書く（値は自分のキー）:

```
GEMINI_API_KEY=あなたのキー
GEMINI_MODEL=gemini-2.0-flash
```

3. 起動:

```powershell
python manage.py migrate
python manage.py runserver
```

http://127.0.0.1:8000/ を開き、新規登録から利用します。  
キー未設定でもアプリは起動しますが、要約時にエラーメッセージが出ます。

## テスト

```powershell
python manage.py test summaries
```

## 本番デプロイ（Render）

既存アプリと同様、別リポジトリ・別 Web サービスで作成します。  
PostgreSQL は有料／新規無料インスタンスの方針に合わせて用意し、論理 DB `summory` を使う想定です。

| 項目 | 値 |
|------|-----|
| Build Command | `./build.sh` |
| Start Command | `gunicorn config.wsgi:application` |

環境変数例: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=.onrender.com`, `DATABASE_URL`, **`GEMINI_API_KEY`**, `GEMINI_MODEL`
