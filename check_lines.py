
with open(r"c:\Users\gaogen\DrissionPage\crawl_1688.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i in range(312, 318):
        print(f"{i+1}: {repr(lines[i])}")
