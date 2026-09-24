---
name: vuln-scanner
description: Web应用漏洞挖掘工作流，覆盖SQL注入、XSS、SSRF、命令执行、未授权访问等常见漏洞的识别、分析与报告生成。当用户提供URL/目标进行安全测试、代码审计或渗透测试时触发。Make sure to use this skill whenever the user mentions 漏洞挖掘、漏洞扫描、渗透测试、SQL注入、XSS、SSRF、安全测试、Web漏洞、bug bounty、代码审计、安全审计, even if they don't explicitly ask for vulnerability scanning.
---

# Web应用漏洞挖掘工作流

## 适用场景

本skill用于Web应用的安全测试和漏洞挖掘，适用于：
- 对目标URL进行黑盒渗透测试
- 审计源代码中的安全漏洞
- Bug bounty狩猎
- 企业内部安全评估
- CTF比赛中的Web类题目

**前置条件**：必须获得目标的**授权测试许可**。未经授权的测试属于违法行为。

## 工作流程

### 阶段1：信息收集

收集目标的基础信息，建立攻击面图谱。

**关键动作**：
1. **基础信息**
   - 域名/IP、端口开放情况
   - 技术栈识别（Server头、响应头、错误页面特征）
   - WAF/CDN识别

2. **资产发现**
   - 子域名枚举
   - 目录/文件爆破（如 `dirsearch`、`gobuster`）
   - API端点识别（Swagger、API文档泄露）

3. **输入点识别**
   - URL参数（GET/POST）
   - HTTP头（User-Agent、Referer、X-Forwarded-For）
   - Cookie
   - JSON/XML body字段
   - 文件上传点

**工具推荐**：Burp Suite、curl、nmap、whatweb、wappalyzer

**输出**：目标信息清单（保存到 `output/<target>/recon.md`）

### 阶段2：漏洞扫描

按漏洞类型系统化排查。

**核心漏洞清单**（详见 `references/vuln-catalog.md`）：

| 漏洞类型 | 严重程度 | 排查优先级 |
|---------|---------|-----------|
| SQL注入 | 高危 | P0 |
| 命令执行/RCE | 高危 | P0 |
| SSRF | 高危 | P0 |
| 未授权访问 | 高危 | P0 |
| 文件上传 | 高危 | P0 |
| XSS（存储型） | 中危 | P1 |
| CSRF | 中危 | P1 |
| IDOR | 中危 | P1 |
| XXE | 中危 | P1 |
| XSS（反射型） | 低危 | P2 |
| 信息泄露 | 低危 | P2 |

**扫描策略**：
- 先手工测试关键参数，再使用工具辅助
- 每个漏洞类型遵循：识别 → 验证 → 危害评估 → 利用 三步骤
- 参考 `references/payloads.md` 获取测试payload

**工具推荐**：SQLMap、Burp Suite Scanner、Xray、AWVS、Nuclei

**输出**：漏洞列表（保存到 `output/<target>/findings.md`）

### 阶段3：漏洞验证

确认漏洞真实可利用，排除误报。

**验证要点**：
1. **重现性**：多次请求结果一致
2. **影响范围**：是否影响真实数据
3. **利用复杂度**：是否需要特殊条件（认证、特殊Header）
4. **危害程度**：结合业务场景评估实际影响

**常见误报特征**：
- WAF拦截导致的payload响应
- 测试环境与生产环境配置差异
- 输入被前端JS过滤但后端未过滤

### 阶段4：报告生成

使用标准化模板生成漏洞报告。

**报告模板**：参见 `assets/report-template.md`

**报告结构**：
1. 漏洞概述
2. 风险等级（CVSS评分）
3. 漏洞详情（URL、参数、payload）
4. 复现步骤
5. 危害说明
6. 修复建议
7. 参考资料

详细模板使用说明见 `assets/report-template.md`。

### 阶段5：报告输出

**输出文件清单**：
- `output/<target>/recon.md` - 信息收集结果
- `output/<target>/findings.md` - 漏洞列表
- `output/<target>/report_<vuln-id>.md` - 单个漏洞详细报告
- `output/<target>/summary.md` - 总体安全评估报告

## 漏洞排查速查

### SQL注入排查

**识别特征**：
- 参数拼接动态SQL
- 错误信息泄露数据库类型
- 参数类型为字符串/数字/日期

**测试payload**（详细见 `references/payloads.md`）：
```
' OR '1'='1
" OR "1"="1
' UNION SELECT NULL,NULL--
1' AND SLEEP(5)--
```

**确认方法**：
- 布尔盲注：响应内容差异
- 时间盲注：响应时间差异
- 报错注入：错误信息泄露
- 联合注入：UNION返回数据

### XSS排查

**识别特征**：
- 用户输入回显到HTML页面
- 未对特殊字符进行HTML实体编码

**测试payload**：
```
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
javascript:alert(1)
```

**确认方法**：
- 浏览器开发者工具查看DOM
- 触发事件（如onerror）确认执行

### SSRF排查

**识别特征**：
- 参数包含URL或IP地址
- 服务端请求外部资源

**测试payload**：
```
http://127.0.0.1
http://169.254.169.254/  # AWS元数据
file:///etc/passwd
dict://127.0.0.1:6379
```

**确认方法**：
- 响应包含内部服务内容
- 通过Burp Collaborator验证出网

### 命令执行排查

**识别特征**：
- 参数拼接到系统命令
- 调用exec/system/popen等函数

**测试payload**：
```
; ls
| whoami
` id `
$(cat /etc/passwd)
```

**确认方法**：
- 命令执行结果回显
- 时间延迟验证（sleep 5）

### 未授权访问排查

**识别特征**：
- API端点缺少鉴权检查
- 越权访问他人资源

**测试方法**：
- 移除Cookie/Token重放请求
- 修改ID参数测试水平越权
- 提升权限测试垂直越权

**确认方法**：
- 成功访问他人数据
- 执行管理员操作

## 工具使用建议

### 主动扫描工具

- **SQLMap**：自动化SQL注入检测
  ```bash
  sqlmap -u "http://target.com/page?id=1" --batch
  ```

- **Xray**：综合性漏洞扫描
  ```bash
  xray webscan --basic-crawler http://target.com
  ```

- **Nuclei**：基于模板的扫描
  ```bash
  nuclei -u http://target.com -t vulnerabilities/
  ```

### 被动分析工具

- **Burp Suite**：拦截、修改、重放HTTP请求
- **浏览器开发者工具**：分析前端JS、Cookie、请求

## 最佳实践

### DO（应该做）

✅ 始终确认测试授权
✅ 使用结构化方法系统化排查
✅ 详细记录复现步骤
✅ 提供具体的修复建议
✅ 关注业务影响而非仅技术漏洞
✅ 测试关键功能优先（登录、支付、数据查询）

### DON'T（不应该做）

❌ 不要在未授权情况下测试
❌ 不要执行破坏性操作（删除数据、修改密码）
❌ 不要在生产环境使用高危payload
❌ 不要遗漏修复建议
❌ 不要忽视低危漏洞（信息泄露可能成为攻击链一环）

## 进阶参考

- 详细的payload库：参见 `references/payloads.md`
- 完整漏洞目录：参见 `references/vuln-catalog.md`
- 报告模板：参见 `assets/report-template.md`
- 报告生成脚本：参见 `scripts/gen_report.py`

## 输出示例

执行 `分析 http://example.com 的安全漏洞` 时，输出：

```
[阶段1: 信息收集]
- 目标: http://example.com
- 技术栈: Nginx + PHP + MySQL
- 已识别输入点: 23个
- 收集结果: output/example.com/recon.md

[阶段2: 漏洞扫描]
- 扫描漏洞类型: 12类
- 发现可疑点: 8个
- 漏洞列表: output/example.com/findings.md

[阶段3: 漏洞验证]
- 已确认漏洞: 5个
- 高危: 2个
- 中危: 2个
- 低危: 1个

[阶段4: 报告生成]
- 总体报告: output/example.com/summary.md
- 单个漏洞报告:
  - report_sqli_001.md
  - report_xss_002.md
  - ...

[阶段5: 输出]
- 报告已保存到 output/example.com/ 目录
```

## 注意事项

⚠️ **法律声明**：本skill仅用于合法的安全测试场景。使用者需自行确保已获得目标的书面授权，所有测试行为需符合当地法律法规。

⚠️ **测试原则**：
- 测试前确认授权范围
- 测试中避免影响生产环境
- 测试后及时报告并协助修复
- 不保留敏感数据

⚠️ **负责任披露**：发现的漏洞应通过正规渠道报告给目标方，避免公开披露细节直至漏洞修复完成。