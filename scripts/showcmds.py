import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(ROOT, "results", "commands.log"), encoding="utf-8").read().splitlines()
i = max(k for k, l in enumerate(L) if "retry after fixing dwebp" in l)
root = "<project>\\"
for l in L[i:]:
    l = l[20:].replace(root, "")
    l = re.sub(r"work\\tools\\\S*\\", "", l)
    if re.search(r"_q(62|68|44|50)[._]", l):
        print(l)
    elif "summer-tanager_JXL_dist" in l or "summer-tanager_AVIF_dist" in l:
        print(l)
