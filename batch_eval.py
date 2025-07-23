import subprocess

def run_game():
    result = subprocess.run(
        ["python", "go_play.py", "-n=5", "-p1=my_player3", "-p2=best_my_player", "-t=0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = result.stdout

    if "胜者：X" in output or "Player 1 获胜" in output:
        return "my_player3"
    elif "胜者：O" in output or "Player 2 获胜" in output:
        return "best_my_player"
    elif "平局" in output or "Tie" in output:
        return "tie"
    else:
        return "error"

num_games = 100
wins = 0
losses = 0
ties = 0
errors = 0

for i in range(num_games):
    outcome = run_game()
    if outcome == "my_player3":
        wins += 1
    elif outcome == "best_my_player":
        losses += 1
    elif outcome == "tie":
        ties += 1
    else:
        errors += 1

print(f"总对局数: {num_games}")
print(f"胜利局数: {wins} | 正确率: {wins/num_games:.2%}")
print(f"失败局数: {losses} | 错误率: {losses/num_games:.2%}")
print(f"平局局数: {ties}")
if errors > 0:
    print(f"⚠️ 错误局数: {errors}")
