# softtennis_club
ソフトテニス部の部員、練習メニュー管理、AI相談が可能です。

##概要
ソフトテニス部の部員・練習メニューを管理し、練習メニューをAIに相談できるWebアプリです。
本アプリではGoogle Gemini APIキーを使用します。

##機能
-メンバーの一覧表示・登録・削除
-練習メニューの一覧表示・登録・削除
-練習メニューをAIに相談機能

##使用技術
-Python(Flask)
-HTML
-SQLite3
-CSV

##ファイル構成
templates/
|-ai.html
|-index.html
|-menu.html
|-players.html
club.db 
club.ipynb
club_app.py
menu.csv
player.csv
position.csv
README.md

##実行方法
1.Pythonをインストール
2.softtennis_clubをダウンロード
3.club.ipynbを実行し、コメントアウトの部分を実行してDBにテーブルが作成できているか確認
4.GoogleでAPIキーを取得
5.コマンドプロンプトで"setx GOOGLE_API_KEY "ここにあなたのAPIキー""を実行
6.club_app.pyを実行し、ブラウザでアクセス

##作成者
Misa-313
