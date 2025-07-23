import subprocess

def run_game():
    # 调用一场对局，返回胜者
    result = subprocess.run(
        ["python", "go_play.py", "-n=5", "-p1=my_player", "-p2=random_player", "-t=0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = result.stdout

    # 判定胜者：根据输出结尾分析
    if "胜者：X" in output:
        return "my_player"
    elif "胜者：O" in output:
        return "random_player"
    elif "Tie" in output or "平局" in output:
        return "tie"
    else:
        return "error"

# 运行50局
num_games = 50
wins = 0
losses = 0
ties = 0
errors = 0

for i in range(num_games):
    outcome = run_game()
    if outcome == "my_player":
        wins += 1
    elif outcome == "random_player":
        losses += 1
    elif outcome == "tie":
        ties += 1
    else:
        errors += 1

# 输出统计结果
print(f"总对局数: {num_games}")
print(f"胜利局数: {wins} | 正确率: {wins/num_games:.2%}")
print(f"失败局数: {losses} | 错误率: {losses/num_games:.2%}")
print(f"平局局数: {ties}")
if errors > 0:
    print(f"⚠️ 错误局数: {errors}")
