import json
import os

DATA_FILE = "pingpong_data.json"

# 讀取或初始化資料
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"matches": []}

# 存檔
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 記錄一場新比賽
def add_match(data):
    print("\n--- 📝 記錄新比賽 ---")
    player1 = input("輸入玩家 1 名字: ")
    score1 = int(input(f"輸入 {player1} 的分數: "))
    player2 = input("輸入玩家 2 名字: ")
    score2 = int(input(f"輸入 {player2} 的分數: "))

    winner = player1 if score1 > score2 else player2
    if score1 == score2:
        winner = "平手"

    match_record = {
        "player1": player1, "score1": score1,
        "player2": player2, "score2": score2,
        "winner": winner
    }
    
    data["matches"].append(match_record)
    save_data(data)
    print(f"✅ 紀錄成功！本場勝者：{winner}")

# 計算並顯示勝率
def show_stats(data):
    print("\n--- 📊 選手勝率統計 ---")
    matches = data["matches"]
    if not matches:
        print("目前沒有任何比賽紀錄。")
        return

    stats = {}
    # 統計勝場與參賽場次
    for m in matches:
        for p in [m["player1"], m["player2"]]:
            if p not in stats:
                stats[p] = {"wins": 0, "total": 0}
            stats[p]["total"] += 1
        
        if m["winner"] != "平手":
            stats[m["winner"]]["wins"] += 1

    # 印出結果
    for player, stat in stats.items():
        win_rate = (stat["wins"] / stat["total"]) * 100
        print(f"👤 {player}: 參賽 {stat['total']} 場 | 勝 {stat['wins']} 場 | 勝率 {win_rate:.1f}%")

# 主程式選單
def main():
    data = load_data()
    while True:
        print("\n🏓 桌球數據追蹤器 🏓")
        print("1. 記錄新比賽")
        print("2. 查看選手勝率")
        print("3. 離開程式")
        
        choice = input("請選擇功能 (1/2/3): ")
        
        if choice == "1":
            add_match(data)
        elif choice == "2":
            show_stats(data)
        elif choice == "3":
            print("👋 掰掰！")
            break
        else:
            print("⚠️ 輸入錯誤，請重新選擇。")

if __name__ == "__main__":
    main()
