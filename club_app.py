import sqlite3
from flask import Flask, render_template, request, redirect
import os
import google.generativeai as genai

#AI設定
api = os.getenv("GOOGLE_API_KEY")
if api is None:
    print("APIキーが設定されていません")
else:
    print("APIキー取得OK")

genai.configure(api_key = api)
model = genai.GenerativeModel("gemini-2.5-flash")


#アプリ作成
app = Flask(__name__)

#トップ
@app.route("/")
def index():
    return render_template("index.html")

#メンバー管理
@app.route("/players")
def players():
    sort = request.args.get("sort", "normal")

    conn = sqlite3.connect("club.db")
    cur = conn.cursor()

    sql = """
    SELECT player.id_pl, player.name, position.position
    FROM player
    JOIN position ON player.id_posi = position.id_posi
    """

    if sort == "fw":
        sql += " ORDER BY player.id_posi ASC"
    elif sort == "bw":
        sql += " ORDER BY player.id_posi DESC"

    cur.execute(sql)
    players = cur.fetchall()
    conn.close()

    return render_template("players.html", players = players)

#メンバー登録
@app.route("/players/add", methods=["POST"])
def add_player():
    id_pl = request.form["id_pl"]
    name = request.form["name"]
    position = request.form["position"]

    conn = sqlite3.connect("club.db")
    cur = conn.cursor()

    #ポジション名をid_posiに変換してDBに登録
    cur.execute("SELECT id_posi FROM position WHERE position = ?", (position,))
    id_posi = cur.fetchone()[0]
    cur.execute("INSERT INTO player (id_pl, name, id_posi) VALUES (?, ?, ?)", (id_pl, name, id_posi))
    conn.commit()
    conn.close()

    return redirect("/players")

#メンバー削除
@app.route("/players/delete/<id_pl>")
def delete_player(id_pl):
    conn = sqlite3.connect("club.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM player WHERE id_pl = ?", (id_pl,))

    conn.commit()
    conn.close()

    return redirect("/players")

#メニュー管理
@app.route("/menu")
def menu():
    filter_posi = request.args.get("filter", "allshow")

    conn = sqlite3.connect("club.db")
    cur = conn.cursor()

    sql = """
    SELECT menu.id_m, menu.menu_name, position.position, menu.memo
    FROM menu
    JOIN position ON menu.id_posi = position.id_posi
    """

    if filter_posi == "fw":
        sql += " WHERE position.position = '前衛'"
    elif filter_posi == "bw":
        sql += " WHERE position.position = '後衛'"
    elif filter_posi == "all":
        sql += " WHERE position.position = '全員'"

    cur.execute(sql)
    menu = cur.fetchall()
    conn.close()

    return render_template("menu.html", menu = menu)

#メニュー登録
@app.route("/menu/add", methods=["POST"])
def add_menu():
    menu_name = request.form["menu_name"]
    position = request.form["position"]
    memo = request.form["memo"]
    if memo == "":
        memo = None

    conn = sqlite3.connect("club.db")
    cur = conn.cursor()

    #ポジション名をid_posiに変換してDBに登録
    cur.execute("SELECT id_posi FROM position WHERE position = ?", (position,))
    id_posi = cur.fetchone()[0]

    cur.execute("SELECT MAX(id_m) FROM menu")
    last_id = cur.fetchone()[0]

    if last_id is None:
        id_m = "m0001"
    else:
        num = int(last_id[1:])
        id_m = f"m{num+1:04d}"

    cur.execute("INSERT INTO menu (id_m, menu_name, id_posi, memo) VALUES (?, ?, ?, ?)", (id_m, menu_name, id_posi, memo))
    conn.commit()
    conn.close()

    return redirect("/menu")

#メンバー削除
@app.route("/menu/delete/<id_m>")
def delete_menu(id_m):
    conn = sqlite3.connect("club.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM menu WHERE id_m = ?", (id_m,))

    conn.commit()
    conn.close()

    return redirect("/menu")

#AI相談
@app.route("/ai", methods = ["GET", "POST"])
def ai():
    reply = ""

    conn = sqlite3.connect("club.db")
    cur = conn.cursor()

    cur.execute("""
                SELECT menu.menu_name, position.position, menu.memo
                FROM menu
                JOIN position ON menu.id_posi = position.id_posi
            """)
    
    menus = cur.fetchall()
    conn.close()

    # AIに送る文章を作る
    menu_text = ""
    for m in menus:
        menu_text += f"・{m[0]}（対象:{m[1]}） メモ:{m[2]}\n"


    if request.method == "POST":
        opinion = request.form["opinion"]

        prompt = menu_text + f"""
        あなたはソフトテニス部のコーチです。
        以下の【練習メニュー】だけを使って、【相談内容】に合った練習メニューを作成してください。

        【ルール】
        ・menu_textの中から選んで練習メニューを作成し、表にしてわかりやすくまとめること
        ・練習メニューの横にそのメニューを何分間行うか、何回行うか(球出しと打つ人交代など)を書くこと
        ・勝手に新しいメニューを作成しないこと
        ・前置きや長い説明文を書かず、練習メニューの最後にアドバイスを書くこと
        ・一行に1メニューで出力すること
        ・30分に5分程度休憩をとること
        ・最後は休憩ではなく練習で終えること
        ・以下の例にのっとって出力すること

        【出力の例】
        <練習メニュー>
        ボレーボレー　　　3分×2
        ショート乱打　　　3分×2
        ロブ乱打　　　　　3分×2

        --休憩　5分--

        手出しの一本打ち　15分　　打つ人がコース指定、手出しで10球交代
        サーブ練　　　　　4分×2
        サーブレシーブ　　7分×2

        <アドバイス>
        意識することを練習前に伝えてから練習開始すること

        【練習メニュー】
        {menu}

        【相談内容】
        {opinion}
        """
        response = model.generate_content(prompt)
        reply = response.text
    return render_template("ai.html", reply = reply)

if __name__ == "__main__":
    app.run(debug = True)