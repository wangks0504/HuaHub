import requests

def build_headers(referer=None):
    headers = {
        "Host": "jwzx.usc.edu.cn:8924",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    if referer:
        headers["Referer"] = referer
    return headers

# ✅ 使用 Session 自动管理 Cookie（自动保留多个 JSESSIONID）
session = requests.Session()

# ✅ Step 0: 主动访问首页，让服务器分配初始 JSESSIONID（Path=/）
home_url = "http://jwzx.usc.edu.cn:8924/"
home_resp = session.get(home_url, headers=build_headers())
print("✅ 第一步：访问首页，状态码 =", home_resp.status_code)
for cookie in session.cookies:
    print(f"🔸 Cookie: {cookie.name} = {cookie.value} (Path={cookie.path})")

# ✅ Step 1: 获取 scode 和 sxh
sess_url = "http://jwzx.usc.edu.cn:8924/Logon.do?method=logon&flag=sess"
sess_resp = session.post(sess_url, headers=build_headers(referer=home_url))
if sess_resp.status_code != 200:
    print("❌ 获取加密规则失败")
    exit()

result = sess_resp.text.strip().split("#")
if len(result) != 2:
    print("❌ 返回格式异常：", sess_resp.text)
    exit()
scode, sxh = result
print("✅ scode =", scode)
print("✅ sxh   =", sxh)

# ✅ Step 2: 构造 encoded
user_account = "20234550302"
user_password = "8172170613Oo"
code = user_account + "%%%" + user_password
encoded = ""
for i in range(len(code)):
    if i < 20:
        insert_len = int(sxh[i])
        encoded += code[i] + scode[:insert_len]
        scode = scode[insert_len:]
    else:
        encoded += code[i:]
        break
print("✅ encoded =", encoded)

# ✅ Step 3: 正式登录
login_url = "http://jwzx.usc.edu.cn:8924/Logon.do?method=logon"
payload = {
    "userAccount": user_account,
    "userPassword": user_password,
    "encoded": encoded
}
login_resp = session.post(login_url, data=payload, headers=build_headers(referer=login_url), allow_redirects=False)
print("✅ 登录响应状态码:", login_resp.status_code)
print("✅ 登录响应内容前500字:\n", login_resp.text[:500])

print("\n✅ 当前 Session 中 Cookies：")
for cookie in session.cookies:
    print(f"- {cookie.name} = {cookie.value} (Path={cookie.path})")

# ✅ Step 4: 跟进跳转
if login_resp.status_code == 302:
    redirect_url = login_resp.headers.get("Location")
    print("➡ 第一步重定向地址:", redirect_url)

    second_resp = session.get(redirect_url, headers=build_headers(referer=login_url), allow_redirects=False)
    if second_resp.status_code == 302:
        final_url = second_resp.headers.get("Location")
        print("➡ 第二步重定向地址:", final_url)

        final_resp = session.get(final_url, headers=build_headers(referer=redirect_url))
        print("✅ 最终学生首页状态码:", final_resp.status_code)
        print("✅ 页面内容前500字符:\n", final_resp.text[:500])

        print("\n✅ 最终 Session 中 Cookies：")
        for cookie in session.cookies:
            print(f"- {cookie.name} = {cookie.value} (Path={cookie.path})")
    else:
        print("⚠ 第二跳未重定向，可能已直接进入主页")
else:
    print("❌ 登录失败或未发生重定向")
