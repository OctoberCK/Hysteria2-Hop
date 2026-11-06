# HCloudLab · 3X-UI Hysteria2 端口跳跃 V1 — Debian 12 / Ubuntu 24.04

## 适用范围

- 3X-UI 面板中的 Hysteria2 入站：数据库 `protocol=hysteria`
- 在面板填写 **Hop Ports**，例如 `20000-30000`；脚本只读数据库，不修改 x-ui.db。
- 支持 Debian 12、Ubuntu 24.04，要求以 systemd 启动；IPv4，存在全局 IPv6 地址时也创建 IPv6 规则。
- UFW 开启时自动添加跳跃范围 **和 Hysteria2 实际监听端口** 的 UDP 放行规则；nftables 未安装时从当前系统配置的 apt 软件源自动安装。
  - 这里说的是服务器自身的 UFW，不是 DMIT/其他云厂商控制台里的"安全组"。安全组仍需自己在面板放行跳跃范围和监听端口。
- 本版本不保证与 Docker 或其他自定义 NAT 规则共存；检测到其他 DNAT/redirect 将安全拒绝安装。

## 🎧 图文配置教程

[🎧 3X-UI Hysteria2 端口跳跃配置教程（面板参数、Shadowrocket、脚本命令）](docs/🎧-Hysteria2端口跳跃配置.md)

## 安装此 Debian 12 兼容版

此分支由 [OctoberCK/Hysteria2-Hop](https://github.com/OctoberCK/Hysteria2-Hop) 维护，基于 [hcloudlab/Hysteria2-Hop](https://github.com/hcloudlab/Hysteria2-Hop) 增加 Debian 12 兼容。

已有 3X-UI 和启用的 Hysteria2 入站，并填写 Hop Ports 后，可在线安装：

```bash
# 使用 root 登录时省略 sudo；精简系统先补齐依赖。
sudo apt-get update
sudo apt-get install -y python3 iproute2 curl ca-certificates
curl -fL --retry 3 -o /tmp/hy2hop-bootstrap.sh https://raw.githubusercontent.com/OctoberCK/Hysteria2-Hop/main/bootstrap.sh
sudo bash /tmp/hy2hop-bootstrap.sh
```

也可把此修改版的完整目录上传、解压到服务器，进入包含 `install.sh` 和 `hy2hop.py` 的目录后执行：

```bash
# 使用 root 登录时省略 sudo；精简系统先补齐依赖。
sudo apt-get update
sudo apt-get install -y python3 iproute2 ca-certificates
sudo bash install.sh
```

也可以直接传入操作及入站 ID：

```bash
sudo bash install.sh install --inbound-id 5
sudo /usr/local/sbin/hcloudlab-hy2hop status
sudo /usr/local/sbin/hcloudlab-hy2hop update
sudo /usr/local/sbin/hcloudlab-hy2hop restore
```

`5` 仅为示例，按实际入站 ID 修改。首次运行不带参数会显示菜单。安装后执行 `/usr/local/sbin/hcloudlab-hy2hop` 可再次打开菜单。

`bootstrap.sh` 从本 fork 的 `main/hy2hop.py` 下载兼容版。上游 hcloudlab 的安装地址仍下载原版，请使用上述 OctoberCK 地址或本地 `install.sh`。

Debian 未安装或未开启 UFW 时，脚本不会安装或开启它；已有自定义 nftables/iptables 过滤策略及云安全组需自行允许跳跃范围和实际监听端口的 UDP。

## Debian 12 兼容修改与验证

- 系统检查接受 Debian `ID=debian` / `VERSION_ID=12`，保留 Ubuntu 24.04；支持 os-release 中带引号的值，其他发行版/版本仍会拒绝。
- 仅使用 Python 标准库，无需 pip 或 `--break-system-packages`。Debian 12 的默认 Python 为 [3.11](https://packages.debian.org/bookworm/python3)。
- 系统命令使用 `LC_ALL=C`，避免 UFW 的本地化输出导致状态误判。
- systemd 服务新增 `After=nftables.service`；Debian 的 [nftables 服务](https://sources.debian.org/src/nftables/1.0.6-2%2Bdeb12u2/debian/nftables.service/) 会加载全局规则，应先完成该步骤再加载本工具的专属表。
- 本地安装脚本支持传参；bootstrap 运行结束后清理临时目录。
- 当前验证：Windows Python 3.10 下 38 项 mock/SQLite 测试通过；仅为导入 Linux 专用模块提供了 `fcntl` 占位，测试未调用真实文件锁。Python 编译和 Bash 语法检查通过。
- 已添加 Debian 12 / Ubuntu 24.04 容器 CI，运行系统 Python 的测试，以及真实 IPv4/IPv6 nftables 规则检查、加载、清理；**此 CI 尚未运行**，容器测试也不代表 systemd 启动、重启或公网客户端验证。
- **此修改版尚未在 Debian 12 VPS 上完成安装、更新、恢复、重启及客户端连通性实测。** 请按下方验收步骤检查；`status PASS` 只表示本机配置检查通过。

## VPS / ISP 推荐

以下服务可按实际需求选用，**不是使用 Hysteria2-Hop 的必要条件**。

| 名称 | 主要特点 | 链接 |
| --- | --- | --- |
| **搬瓦工 VPS — DC9** | **CN2 GIA + CMIN2 + 联通 Premium**，面向中国大陆方向提供多运营商优质线路；当前推荐套餐 **$49.99 / 季度**。 | [购买 DC9](https://bwh81.net/aff.php?aff=82473&a=add&pid=87&billingcycle=quarterly&configoption%5B17%5D=55) |
| **DMIT** | **CN2 GIA 顶级线路，国内访问速度一流**。 | [访问 DMIT](https://www.dmit.io/aff.php?aff=20932) |
| **Proxy-Seller ISP** | 静态住宅代理 ISP，价格约 **$3 / 月起**；优惠码 **HCLOUD15**。 | [购买 ISP](https://proxy-seller.com/?partner=8Y51DM71OGR26N) |

> 以上为 Affiliate 推广链接，可能为项目维护者带来佣金。Hysteria2-Hop 只负责 3X-UI Hysteria2 的端口跳跃规则，不提供 VPS、线路或 ISP 出口。价格、套餐和优惠以服务商实际页面为准。

## 验收

1. 首次安装：检查是否自动安装 nftables，读取 Hop Ports 并生成 IPv4/IPv6 映射，确认 UFW 同时放行了跳跃范围和实际监听端口（`ufw status numbered`）。
2. `sudo /usr/local/sbin/hcloudlab-hy2hop status`：检查当前配置；缺少监听端口或跳跃范围的任一条 UFW 规则都应报告 `STATUS: FAIL`。
3. 更新客户端订阅，真实连接并确认跳跃端口的 UDP 流量计数增加。
4. 连续执行 `update` 3 次，确保没有重复规则。
5. 重启 VPS，再执行 `status`，验证客户端仍可连接。
6. 在 3X-UI 修改监听端口和/或 Hop Ports，再执行 `update`，检查旧端口/旧范围的 UFW 规则消失、新端口/新范围的规则生效。
7. 执行 `restore`，确认原 443/UDP 节点可用、其他防火墙规则不变（包括安装前已存在的 UFW 规则）。
8. 出现错误立即停止并提供完整终端输出；不要手工执行 `nft flush ruleset` 或关闭 UFW。

## 上游原有验证记录（本次未复测）

- Python 语法检查与 31 项 mock/SQLite 自动化测试通过（新增跳跃范围 + 监听端口双 UFW 规则的安装/更新/恢复/状态检查/旧版本升级/失败回滚用例）。
- 在隔离的 Ubuntu 24.04 容器中，用真实 `ss`/`nft`/`ufw`/`apt-get` 命令（非 mock）端到端跑通了完整的
  `install → status → update ×3（确认幂等、规则不重复）→ restore` 流程，并单独确认：
  - `apt-get install nftables` 在全新安装时不会自动启用/启动 `nftables.service`；
  - `ufw`/`nft -a list ruleset` 的真实输出格式与代码里的字符串匹配、正则解析完全一致；
  - 存在其他 DNAT/redirect 规则时能正确检测并拒绝安装，自身规则不会被误判为冲突。
- **已在 DMIT Ubuntu 24.04 实机验证**（修复前的基础功能）：3X-UI Hysteria2 入站、Shadowrocket IPv4 端口跳跃连接、修改 Hop Ports 后执行 `update`、重复 `update` 幂等，以及 VPS 重启后服务与客户端连通性。**尚未完成公网 IPv6 双栈连通性验证。** `status PASS` 仅代表本机配置检查通过。
- **本次新增的"监听端口 UFW 放行"修复尚未在 DMIT 实机复测**：目前只验证了本地 mock 测试中实际执行的 `ufw`/`nft` 命令字符串和状态文件逻辑，没有在真实 DMIT + 3X-UI + UFW/nftables 环境中重新跑过 install → status → update → restore 全流程，也没有用真实客户端确认监听端口位于跳跃范围之外时的连接恢复。
- 跨 nftables/UFW/systemd 的自动回滚实现了尽力清理；断电、SIGKILL、外部系统同时修改规则等情况下，不能保证严格事务原子性。
- 恢复不卸载 nftables 软件包，不修改 3X-UI 数据库。

