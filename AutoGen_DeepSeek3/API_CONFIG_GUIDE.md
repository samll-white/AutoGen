# API配置指南

当遇到 OpenAI 配额不足错误时，可以切换到其他API服务商。

## 🚨 常见错误

```
Error code: 429 - You exceeded your current quota
```

这表示OpenAI账户余额不足。

---

## 🔧 解决方案：切换API服务商

### 方案1：智谱AI (推荐) 🇨🇳

**优点**：
- ✅ 注册简单（手机号）
- ✅ 新用户免费额度
- ✅ 支付宝/微信支付
- ✅ 国内访问快

**配置步骤**：

1. **注册账号**：https://open.bigmodel.cn/
2. **获取API密钥**：登录后在控制台创建
3. **修改 .env 文件**：

```env
LLM_MODEL_ID="glm-4"
LLM_API_KEY="YOUR-ZHIPU-API-KEY"
LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
LLM_TIMEOUT=60
```

**可用模型**：
- `glm-4` - 最新版本，性能最强
- `glm-4-flash` - 快速版本，便宜
- `glm-3-turbo` - 经济版本

---

### 方案2：阿里通义千问 🇨🇳

**优点**：
- ✅ 阿里云生态
- ✅ 新用户免费额度
- ✅ 稳定可靠

**配置步骤**：

1. **注册**：https://dashscope.aliyun.com/
2. **获取API密钥**
3. **修改 .env 文件**：

```env
LLM_MODEL_ID="qwen-max"
LLM_API_KEY="YOUR-ALIYUN-API-KEY"
LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_TIMEOUT=60
```

**可用模型**：
- `qwen-max` - 最强版本
- `qwen-plus` - 平衡版本
- `qwen-turbo` - 快速版本

---

### 方案3：百度文心一言 🇨🇳

**配置步骤**：

1. **注册**：https://cloud.baidu.com/
2. **开通文心一言服务**
3. **获取API Key和Secret Key**
4. **修改 .env 文件**：

```env
LLM_MODEL_ID="ERNIE-4.0-8K"
LLM_API_KEY="YOUR-BAIDU-API-KEY"
LLM_BASE_URL="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
LLM_TIMEOUT=60
```

---

### 方案4：继续使用OpenAI（充值）💳

如果你想继续使用OpenAI：

1. **访问**：https://platform.openai.com/account/billing
2. **充值**：最低$5-$10
3. **支付方式**：国际信用卡（Visa/MasterCard）

**注意**：OpenAI在中国大陆需要科学上网。

---

### 方案5：本地模型 Ollama（完全免费）🆓

**优点**：
- ✅ 完全免费
- ✅ 无需联网
- ✅ 数据隐私

**缺点**：
- ⚠️ 需要较好的显卡（8GB+ VRAM）
- ⚠️ 性能不如云端模型

**安装步骤**：

1. **下载Ollama**：https://ollama.com/
2. **安装模型**：
   ```bash
   ollama pull llama3.1
   ```
3. **修改 .env 文件**：
   ```env
   LLM_MODEL_ID="llama3.1"
   LLM_API_KEY="ollama"
   LLM_BASE_URL="http://localhost:11434/v1"
   LLM_TIMEOUT=60
   ```

---

## 💰 价格对比

| 服务商 | 模型 | 价格/1M tokens | 免费额度 | 充值方式 |
|--------|------|---------------|---------|---------|
| OpenAI | gpt-4o | $2.5-$10 | ❌ | 信用卡 |
| 智谱AI | glm-4 | ¥15-¥100 | ✅ 有 | 支付宝/微信 |
| 通义千问 | qwen-max | ¥2-¥40 | ✅ 有 | 支付宝 |
| 文心一言 | ERNIE-4.0 | ¥12-¥120 | ✅ 有 | 支付宝/微信 |
| Ollama | llama3.1 | 免费 | ✅ 无限 | 无 |

---

## 🎯 推荐选择

### 如果你想：
- **快速开始** → 智谱AI（免费额度，注册简单）
- **最佳性能** → OpenAI gpt-4o（需要充值）
- **完全免费** → Ollama（需要好电脑）
- **国内稳定** → 阿里通义千问

---

## 📝 配置文件位置

修改这个文件：
```
D:\yanjiusheng\class\DeepLearning\LLM\hello-agents-main\AutoGenDemo\.env
```

修改后重新运行：
```bash
python autogen_software_team.py
```

---

## ⚠️ 注意事项

1. **API密钥保密**：不要泄露给他人
2. **监控用量**：定期检查使用情况
3. **设置限额**：避免意外超支

---

## 🔗 相关链接

- OpenAI: https://platform.openai.com/
- 智谱AI: https://open.bigmodel.cn/
- 通义千问: https://dashscope.aliyun.com/
- 文心一言: https://cloud.baidu.com/
- Ollama: https://ollama.com/
