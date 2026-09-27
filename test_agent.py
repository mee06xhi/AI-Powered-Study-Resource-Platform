from app.agent import run_agent

result = run_agent("What are the most repeated topics in the DBMS question papers?")
print("Tool used:", result["tool_used"])
print("Answer:", result["answer"])

# result = run_agent("Find me notes for Database Management Systems, code BCS403")
# print(result["tool_used"])  # should print: search_resources

