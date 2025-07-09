# Fix for agent_executor.invoke() error

# ❌ WRONG WAY (causes error):
# response = agent_executor.invoke("Show all customers with all offers today.")

# ✅ CORRECT WAY - Option 1: Use dictionary with "input" key
response = agent_executor.invoke({"input": "Show all customers with all offers today."})

# ✅ CORRECT WAY - Option 2: If using rag_chain (as shown in your notebook)
# response = rag_chain.invoke("Show all customers with all offers today.")

print(response) 