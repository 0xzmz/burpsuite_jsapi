# burpsuite_jsapi

一个用Python写的用于查找 JS 文件中的 API 接口的 BurpSuite 插件。

### 0x00 使用前提

需安装好 BurpSuite 的 **JPython** 环境，可参考 https://www.freebuf.com/news/193657.html 。

### 0x01 使用步骤

1. ```bash
   git clone https://github.com/0x-zmz/burpsuite_jsapi
   ```

2. 在 **Extender** > **Extensions** 中添加 `burpsuite_jsapi.py` 插件。
   ![install](/install.png)

### 0x02 使用结果

在测试中，可直接点击 JsApi 选项卡获取结果，示例如下图所示：

![example](/example.png)