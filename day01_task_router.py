def search_tool(task):
  return f"正在搜索 {task}"
def calculate_tool(task):
  return f"正在计算 {task}"
def agent_router(task):
  if "搜索" in task:
    return search_tool(task)
  elif "计算" in task:
    return calculate_tool(task)
  else:
    return "无法识别的任务类型"
while True:
  user_input = input("请输入任务:")
  if user_input == "退出":
    print("退出程序")
    break
  result = agent_router(user_input)
  print(result)