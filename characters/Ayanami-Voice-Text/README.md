```bash
cp metadata_aligh.csv metadata.csv
```

# Format

tacotron 需要的格式是：

```
TODO
```

VITS 需要的格式是，每一行为下列数据的 CSV 文件：

| filename        | dialogue_jp                                            |
| --------------- | ------------------------------------------------------ |
| 绫波 unlock.mp3 | 綾波……です。「鬼神」とよく言われるのです。よろしくです |

文件路径相对于 vits 下的 `train.py` 文件。

CSV 文件不需要 header。

e.g.:

```csv
DUMMY1/LJ049-0022.wav|The Secret Service believed that it was very doubtful that any President would ride regularly in a vehicle with a fixed top, even though transparent.
```
