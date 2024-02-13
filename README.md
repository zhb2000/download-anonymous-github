# Download Anonymous GitHub

从 Anonymous GitHub (https://anonymous.4open.science/) 下载整个仓库的内容。

该脚本仅使用 Python 标准库，无需安装额外的依赖。`urllib` 默认使用系统代理，Windows 下为 IE 代理设置，Linux 下为环境变量 `http_proxy` 和 `https_proxy`。

## 使用方法

```shell
python download-anonymous-github.py <url> [<save_dir>] [--skip-existing]
```

参数：

- `<url>`: 仓库的 URL 地址，例如 `https://anonymous.4open.science/r/repo-name`。
- `<save_dir>`: （可选）下载目录，默认为仓库的名称。

选项：

- `--skip-existing`: 跳过下载目录中已有的文件。
- `--help`: 显示帮助信息。
