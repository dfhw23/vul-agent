#!/usr/bin/env python3
"""
漏洞报告生成器

用于将漏洞信息生成标准化报告。
用法：
    python gen_report.py --type single --data '{"id":"VULN-001", ...}' --output report.md
    python gen_report.py --type summary --target example.com
"""

import argparse
import json
import os
import sys
from datetime import datetime


def generate_vuln_id():
    """生成漏洞ID"""
    now = datetime.now()
    return f"VULN-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"


def render_single_report(vuln_data):
    """生成单个漏洞报告"""
    vuln_id = vuln_data.get('id', generate_vuln_id())
    vuln_type = vuln_data.get('type', 'Unknown')
    vuln_name = vuln_data.get('name', 'Unknown Vulnerability')
    severity = vuln_data.get('severity', '中危')
    cvss = vuln_data.get('cvss', '6.5')
    cwe = vuln_data.get('cwe', 'CWE-Unknown')
    owasp = vuln_data.get('owasp', 'N/A')
    status = vuln_data.get('status', '已确认')
    discover_date = vuln_data.get('discover_date', datetime.now().strftime('%Y-%m-%d'))
    reporter = vuln_data.get('reporter', 'Security Tester')

    url = vuln_data.get('url', 'N/A')
    param = vuln_data.get('param', 'N/A')
    method = vuln_data.get('method', 'GET')

    overview = vuln_data.get('overview', '')
    reproduction = vuln_data.get('reproduction', [])
    impact = vuln_data.get('impact', '')
    fix_suggestion = vuln_data.get('fix_suggestion', '')

    report = f"""# {vuln_id} {vuln_name}

## 基本信息

| 项目 | 内容 |
|------|------|
| 漏洞编号 | {vuln_id} |
| 漏洞类型 | {vuln_type} |
| 风险等级 | {severity} |
| CVSS评分 | {cvss} |
| CWE编号 | {cwe} |
| OWASP分类 | {owasp} |
| 漏洞状态 | {status} |
| 发现日期 | {discover_date} |
| 报告日期 | {datetime.now().strftime('%Y-%m-%d')} |
| 测试人员 | {reporter} |

## 漏洞概述

{overview}

## 受影响资产

- URL: `{url}`
- 参数: `{param}`
- HTTP方法: {method}

## 复现步骤

"""

    for i, step in enumerate(reproduction, 1):
        report += f"### 步骤 {i}\n\n"
        report += f"{step.get('description', '')}\n\n"
        if step.get('request'):
            report += f"**请求**:\n```\n{step['request']}\n```\n\n"
        if step.get('response'):
            report += f"**响应**:\n```\n{step['response']}\n```\n\n"

    report += f"""## 危害说明

{impact}

## 修复建议

{fix_suggestion}

## 漏洞状态跟踪

| 状态 | 日期 | 备注 |
|------|------|------|
| 发现 | {discover_date} | 初次发现 |
| 待修复 |  | 待厂商处理 |

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return report


def render_summary_report(target, findings):
    """生成总体评估报告"""
    severity_count = {'严重': 0, '高危': 0, '中危': 0, '低危': 0, '信息': 0}
    for finding in findings:
        sev = finding.get('severity', '低危')
        severity_count[sev] = severity_count.get(sev, 0) + 1

    report = f"""# {target} 安全评估报告

## 报告信息

| 项目 | 内容 |
|------|------|
| 评估目标 | {target} |
| 评估时间 | {datetime.now().strftime('%Y-%m-%d')} |
| 报告日期 | {datetime.now().strftime('%Y-%m-%d')} |
| 报告版本 | v1.0 |

## 执行摘要

### 风险总览

| 风险等级 | 数量 |
|---------|------|
| 严重 | {severity_count['严重']} |
| 高危 | {severity_count['高危']} |
| 中危 | {severity_count['中危']} |
| 低危 | {severity_count['低危']} |
| 信息 | {severity_count['信息']} |

## 漏洞列表

| 编号 | 漏洞名称 | 类型 | 风险等级 |
|------|---------|------|---------|
"""
    for finding in findings:
        report += f"| {finding.get('id', 'N/A')} | {finding.get('name', 'N/A')} | {finding.get('type', 'N/A')} | {finding.get('severity', 'N/A')} |\n"

    report += """
## 修复优先级建议

### P0 - 立即修复
"""
    high_priority = [f for f in findings if f.get('severity') in ['严重', '高危']]
    for f in high_priority:
        report += f"- {f.get('id', 'N/A')}: {f.get('name', 'N/A')}\n"

    report += """
### P1 - 尽快修复
"""
    mid_priority = [f for f in findings if f.get('severity') == '中危']
    for f in mid_priority:
        report += f"- {f.get('id', 'N/A')}: {f.get('name', 'N/A')}\n"

    report += """
### P2 - 计划修复
"""
    low_priority = [f for f in findings if f.get('severity') in ['低危', '信息']]
    for f in low_priority:
        report += f"- {f.get('id', 'N/A')}: {f.get('name', 'N/A')}\n"

    report += f"""
## 整体安全建议

1. 优先修复高危漏洞，避免数据泄露和系统入侵风险
2. 部署WAF进行纵深防御
3. 建立安全开发生命周期（SDL）
4. 定期进行安全评估和渗透测试

## 免责声明

本报告仅作为安全改进参考。所有测试均在授权范围内进行。

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return report


def render_recon_report(target, info):
    """生成信息收集报告"""
    report = f"""# {target} 信息收集报告

## 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 基础信息

- 目标URL: {target}
- IP地址: {info.get('ip', 'N/A')}
- 开放端口: {info.get('ports', 'N/A')}
- 技术栈: {info.get('tech', 'N/A')}
- WAF/CDN: {info.get('waf', 'N/A')}

## 2. 资产发现

### 子域名
{info.get('subdomains', '未发现')}

### 关键路径
{info.get('paths', '未发现')}

## 3. 输入点识别

{info.get('inputs', '未发现')}

## 4. 备注

{info.get('notes', '')}

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return report


def main():
    parser = argparse.ArgumentParser(description='漏洞报告生成器')
    parser.add_argument('--type', required=True, choices=['single', 'summary', 'recon'],
                        help='报告类型')
    parser.add_argument('--data', help='漏洞数据（JSON格式）')
    parser.add_argument('--target', help='目标名称（用于summary和recon）')
    parser.add_argument('--findings', help='漏洞列表（JSON字符串或文件路径）')
    parser.add_argument('--info', help='信息收集数据（JSON）')
    parser.add_argument('--output', required=True, help='输出文件路径')

    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    if args.type == 'single':
        if not args.data:
            print("错误: --data 不能为空", file=sys.stderr)
            sys.exit(1)
        try:
            vuln_data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"错误: JSON解析失败: {e}", file=sys.stderr)
            sys.exit(1)

        report = render_single_report(vuln_data)
    elif args.type == 'summary':
        if not args.target:
            print("错误: --target 不能为空", file=sys.stderr)
            sys.exit(1)
        if args.findings:
            if os.path.isfile(args.findings):
                with open(args.findings, 'r', encoding='utf-8') as f:
                    findings = json.load(f)
            else:
                try:
                    findings = json.loads(args.findings)
                except json.JSONDecodeError as e:
                    print(f"错误: findings JSON解析失败: {e}", file=sys.stderr)
                    sys.exit(1)
        else:
            findings = []
        report = render_summary_report(args.target, findings)
    elif args.type == 'recon':
        if not args.target:
            print("错误: --target 不能为空", file=sys.stderr)
            sys.exit(1)
        if args.info:
            if os.path.isfile(args.info):
                with open(args.info, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            else:
                try:
                    info = json.loads(args.info)
                except json.JSONDecodeError:
                    info = {}
        else:
            info = {}
        report = render_recon_report(args.target, info)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"报告已生成: {args.output}")
    print(f"字数: {len(report)}")


if __name__ == '__main__':
    main()