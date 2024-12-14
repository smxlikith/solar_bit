#!./.venv/bin/python3

d = {'new_node': {'KABNGYESA002': ['127.0.0.1', 8193]}}
print(list(d.get("new_node").keys())[0])