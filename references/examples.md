# 使用示例

通过实际案例演示如何应用本skill进行漏洞挖掘。

## 示例1：单URL漏洞扫描

**用户输入**：
```
扫描 http://testphp.vulnweb.com 的安全漏洞
```

**执行流程**：

### 阶段1：信息收集

```
- 目标: http://testphp.vulnweb.com
- IP: 44.228.249.3
- 技术栈: Nginx + PHP
- WAF: 未发现
- 输入点识别: 15个
```

### 阶段2：漏洞扫描

```
测试类型:
✓ SQL注入 - 发现1处
✓ XSS - 发现3处
✓ CSRF - 发现1处
✓ 信息泄露 - 发现2处
```

### 阶段3：验证结果

| 漏洞 | URL | 类型 | 等级 |
|------|-----|------|------|
| VULN-001 | /artists.php?artist=1 | SQL注入 | 高危 |
| VULN-002 | /search.php | 反射XSS | 中危 |
| VULN-003 | /comment.php | 存储XSS | 高危 |
| VULN-004 | /login.php | CSRF | 中危 |
| VULN-005 | /admin/ | 未授权访问 | 高危 |

### 输出文件

```
output/testphp.vulnweb.com/
├── recon.md                    # 信息收集
├── findings.md                 # 漏洞列表
├── summary.md                  # 总体报告
└── reports/
    ├── vuln_001_sqli.md       # SQL注入详细报告
    ├── vuln_002_xss.md        # XSS详细报告
    ├── vuln_003_xss.md        # 存储XSS详细报告
    ├── vuln_004_csrf.md       # CSRF详细报告
    └── vuln_005_auth.md       # 未授权访问详细报告
```

---

## 示例2：代码审计场景

**用户输入**：
```
审计这段PHP代码：<用户提供的代码>
```

**审计流程**：

```
1. 静态分析
   - 识别用户输入点
   - 识别危险函数
   - 检查数据流

2. 漏洞识别
   - SQL注入: line 23, line 45
   - XSS: line 67
   - 文件包含: line 89

3. 报告输出
   - 总体报告: summary.md
   - 单漏洞报告: 3个
```

---

## 示例3：单个漏洞验证

**用户输入**：
```
验证 http://target.com/page?id=1 是否存在SQL注入
```

**执行流程**：

```
1. 基础探测
   GET /page?id=1' HTTP/1.1
   → 响应500错误，包含SQL错误信息

2. 数据库类型识别
   → MySQL（错误信息包含MySQL关键字）

3. 漏洞确认
   GET /page?id=1' UNION SELECT 1,2,3-- HTTP/1.1
   → 响应包含"2,3"内容 → 联合注入成功

4. 数据提取
   GET /page?id=-1' UNION SELECT database(),version(),user()-- HTTP/1.1
   → 数据库: testdb, 版本: 5.7.34

5. 报告输出
   - vuln_001_sqli.md（高危）
```

---

## 示例4：扫描脚本使用

### 生成单个漏洞报告

```bash
python scripts/gen_report.py --type single \
  --data '{
    "id": "VULN-20260101-001",
    "name": "用户接口SQL注入漏洞",
    "type": "SQL注入",
    "severity": "高危",
    "cvss": "8.5",
    "cwe": "CWE-89",
    "owasp": "A03:2021",
    "url": "http://target.com/api/user/profile",
    "param": "id",
    "method": "GET",
    "overview": "用户查询接口的id参数未进行参数化处理...",
    "reproduction": [
      {
        "description": "正常请求",
        "request": "GET /api/user/profile?id=1",
        "response": "正常返回用户信息"
      },
      {
        "description": "注入测试",
        "request": "GET /api/user/profile?id=1'",
        "response": "SQL语法错误"
      }
    ],
    "impact": "可获取数据库全部数据，包括用户密码",
    "fix_suggestion": "使用参数化查询"
  }' \
  --output output/report.md
```

### 生成总体报告

```bash
# 先生成漏洞列表文件
cat > findings.json << EOF
[
  {
    "id": "VULN-001",
    "name": "SQL注入",
    "type": "SQL注入",
    "severity": "高危"
  },
  {
    "id": "VULN-002",
    "name": "XSS",
    "type": "XSS",
    "severity": "中危"
  }
]
EOF

python scripts/gen_report.py --type summary \
  --target "target.com" \
  --findings findings.json \
  --output output/summary.md
```

### 生成信息收集报告

```bash
python scripts/gen_report.py --type recon \
  --target "target.com" \
  --info '{
    "ip": "1.2.3.4",
    "ports": "80,443",
    "tech": "Nginx + PHP + MySQL",
    "waf": "CloudFlare"
  }' \
  --output output/recon.md
```

---

## 示例5：完整工作流

**完整的安全评估流程**：

```
第1天 - 信息收集
├── 子域名枚举（subfinder、assetfinder）
├── 端口扫描（nmap、masscan）
├── 目录爆破（dirsearch、gobuster）
└── 技术栈识别（whatweb、wappalyzer）

第2天 - 主动扫描
├── 自动化扫描（xray、nuclei、awvs）
├── 手动测试（Burp Suite）
└── Payload测试

第3天 - 漏洞验证
├── 重现测试
├── 利用验证（确保可被攻击）
└── 业务影响评估

第4天 - 报告撰写
├── 单漏洞报告
├── 总体评估报告
└── 修复建议
```

---

## 场景对照表

| 用户输入类型 | 推荐响应 |
|-------------|---------|
| "扫描 http://x.com" | 完整工作流，5阶段全流程 |
| "测试这个URL是否SQL注入" | 单漏洞验证模式 |
| "审计代码..." | 静态分析模式 |
| "生成报告" | 调用gen_report.py |
| "XSS怎么测试" | 引用payloads.md |
| "有哪些高危漏洞" | 引用vuln-catalog.md |
| "生成报告模板" | 引用report-template.md |

---

## 实际输出示例

### recon.md 示例

```markdown
# target.com 信息收集报告

## 收集时间: 2026-09-24 14:30:00

## 1. 基础信息
- 目标URL: http://target.com
- IP地址: 93.184.216.34
- 开放端口: 80, 443, 8080
- 技术栈: Nginx 1.18.0 + PHP 7.4 + MySQL 5.7
- WAF/CDN: 未检测到WAF

## 2. 资产发现
### 子域名
- www.target.com
- api.target.com
- admin.target.com
- dev.target.com

### 关键路径
- /admin/ - 管理后台
- /api/ - API接口
- /upload/ - 文件上传
- /login.php - 登录入口
- /robots.txt
- /sitemap.xml
```

### findings.md 示例

```markdown
# target.com 漏洞列表

## 高危漏洞
1. **SQL注入** - /api/user/profile?id=
2. **未授权访问** - /api/admin/config
3. **存储XSS** - /comment

## 中危漏洞
1. **CSRF** - /api/user/update
2. **IDOR** - /api/order/view?id=

## 低危漏洞
1. **反射XSS** - /search?q=
2. **信息泄露** - /.git/HEAD
```

### 单个漏洞报告示例

```markdown
# VULN-20260924-001 用户接口SQL注入漏洞

## 基本信息
| 项目 | 内容 |
|------|------|
| 漏洞编号 | VULN-20260924-001 |
| 漏洞类型 | SQL注入 |
| 风险等级 | 高危 |
| CVSS评分 | 8.5 |
...

## 复现步骤
### 步骤 1
正常请求
**请求**:
GET /api/user/profile?id=1
**响应**:
正常返回用户信息

### 步骤 2
注入测试
**请求**:
GET /api/user/profile?id=1'
**响应**:
SQL语法错误
...

## 修复建议
使用参数化查询（PreparedStatement）
```