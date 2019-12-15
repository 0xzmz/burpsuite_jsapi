# burpsuite_jsapi
[中文版本(Chinese version)](README.zh-CNmd)

A BurpSuite extension written by Python,used to find API interface in JS file.

### 0x00 Premise

**JPython** environment should be installed in BurpSuite,consult https://www.freebuf.com/news/193657.html .

### 0x01 Step

1. ```bash
   git clone https://github.com/0x-zmz/burpsuite_jsapi
   ```

2. Add `burpsuite_jsapi.py` plug-in in **Extender** > **Extensions** .
   ![install](/install.png)

### 0x02 Result

In the pentest, you can directly click the JsApi tab to obtain the results, as shown in the following figure:

![example](/example.png)