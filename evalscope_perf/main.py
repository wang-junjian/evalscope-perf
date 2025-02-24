import os
import subprocess
import re
import typer
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

from typing import List
from typing_extensions import Annotated


app = typer.Typer()

def run_evalscope(url, model, dataset_path, max_prompt_length, stop, read_timeout, parallel, n):
    cmd = [
        'evalscope', 'perf',
        '--api', 'openai',
        '--url', url,
        '--model', model,
        '--dataset', 'openqa',
        '--dataset-path', dataset_path,
        '--max-prompt-length', str(max_prompt_length),
        '--stop', stop,
        '--read-timeout', str(read_timeout),
        '--parallel', str(parallel),
        '-n', str(n)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)

    # 将输出保存到文件
    dataset_name = dataset_path.split('/')[-1].split('.')[0]
    output_filename = f'{model}_{dataset_name}_p{parallel}.txt'
    with open(output_filename, 'w') as f:
        f.write(result.stdout)

    return result.stdout

def parse_output(output):
    print(output)
    metrics = {}
    patterns = {
        'Average QPS': r'Average QPS:\s+([\d.]+)',
        'Average latency': r'Average latency:\s+([\d.]+)',
        'Throughput': r'Throughput\(average output tokens per second\):\s+([\d.]+)',
        'Failed requests': r'Failed requests:\s+(\d+)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            metrics[key] = float(match.group(1))
    print('📌 Metrics:', metrics)
    return metrics

def setup_chinese_font():
    # 获取字体文件的绝对路径
    font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Hiragino Sans GB.ttc')
    # 添加字体文件
    font_manager.fontManager.addfont(font_path)
    # 设置 matplotlib 默认字体
    plt.rcParams['font.family'] = ['Hiragino Sans GB']
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

@app.command()
def main(
    url: str = typer.Argument(..., help="OpenAI URL"),
    model: str = typer.Argument(..., help="模型名称"),
    dataset_path: str = typer.Argument(..., help="数据集路径"),
    max_prompt_length: int = typer.Option(256, help="最大提示长度"),
    stop: str = typer.Option("<|im_end|>", help="停止标记"),
    read_timeout: int = typer.Option(30, help="读取超时"),
    parallels: Annotated[List[int], "并行数"] = typer.Option([1], help="并行数"),
    n: int = typer.Option(1, help="请求数")
):
    # 设置中文字体
    setup_chinese_font()

    data = {
        'Parallel': [], 
        'Average QPS': [], 
        'Average latency': [], 
        'Throughput': [],
        'Failed requests': []
    }

    for parallel in parallels:
        print(f'Running with parallel={parallel}')
        output = run_evalscope(url, model, dataset_path, max_prompt_length, stop, read_timeout, parallel, n)
        metrics = parse_output(output)
        data['Parallel'].append(parallel)
        data['Average QPS'].append(metrics.get('Average QPS', 0))
        data['Average latency'].append(metrics.get('Average latency', 0))
        data['Throughput'].append(metrics.get('Throughput', 0))
        data['Failed requests'].append(metrics.get('Failed requests', 0))

    # 绘制子图
    fig, axs = plt.subplots(2, 2, figsize=(18, 9))
    fig.suptitle(f'模型: {model}', fontsize=24)
    plt.tight_layout(rect=[0, 0, 1, 0.92])

    axs[0, 0].plot(data['Parallel'], data['Average QPS'], marker='o')
    axs[0, 0].set_title('平均 QPS 与并行数关系')
    axs[0, 0].set_xlabel('并行数')
    axs[0, 0].set_ylabel('平均 QPS')

    axs[0, 1].plot(data['Parallel'], data['Average latency'], marker='o', color='orange')
    axs[0, 1].set_title('平均延迟与并行数关系')
    axs[0, 1].set_xlabel('并行数')
    axs[0, 1].set_ylabel('平均延迟 (秒)')

    axs[1, 0].plot(data['Parallel'], data['Throughput'], marker='o', color='green')
    axs[1, 0].set_title('吞吐量与并行数关系')
    axs[1, 0].set_xlabel('并行数')
    axs[1, 0].set_ylabel('吞吐量 (token/秒)')

    axs[1, 1].plot(data['Parallel'], data['Failed requests'], marker='o', color='red')
    axs[1, 1].set_title('失败请求数与并行数关系')
    axs[1, 1].set_xlabel('并行数')
    axs[1, 1].set_ylabel('失败请求数')

    plt.tight_layout()
    plt.savefig('performance_metrics.png')
    # plt.show()

if __name__ == "__main__":
    app()
