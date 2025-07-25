# AnimalID - Python 库文档

**版本: 0.1.0**

## 目录

1.  [简介](#1-简介)
2.  [核心特性](#2-核心特性)
3.  [安装指南](#3-安装指南)
4.  [快速入门](#4-快速入门)
5.  [详细用法](#5-详细用法)
    *   [初始化生成器](#51-初始化生成器)
    *   [生成ID](#52-生成id)
    *   [校验ID](#53-校验id)
    *   [使用装饰器自动注入ID](#54-使用装饰器自动注入id)
    *   [使用自定义词库](#55-使用自定义词库)
6.  [工作原理：校验和](#6-工作原理校验和)
7.  [API 参考](#7-api-参考)
8.  [安全注意事项](#8-安全注意事项)

---

## 1. 简介

`AnimalID` 是一个 Python 库，用于生成人类可读、易于记忆且可校验的唯一标识符（ID）。

每个 ID 由四个动物名称组成，格式为 `animal1-animal2-animal3-checksum_animal`。与完全随机的字符串（如 UUID）相比，这种格式的 ID 更容易在日志中查找、在团队成员之间口头交流，也更不容易出错。

最关键的是，第四个动物并非随机，而是基于前三个动物和一个秘密密钥计算出的**校验和**。这使得 `AnimalID` 具备了防篡改和防伪造的能力，确保了 ID 的完整性和来源可信。

## 2. 核心特性

*   **人类可读**：生成的 ID（例如 `fox-wolf-bear-lion`）比 `f47ac10b-58cc-4372-a567-0e02b2c3d479` 更易于阅读、记忆和沟通。
*   **校验和保护**：内置校验和机制，可以轻松验证一个 ID 是否有效或被篡改。
*   **安全且防伪造**：依赖一个用户提供的 `secret_key`，只有持有正确密钥的系统才能生成和验证有效的 ID。
*   **易于集成**：提供一个方便的装饰器，可以自动为函数调用生成并注入 `animal_id`，非常适合为请求、任务或日志条目分配追踪ID。
*   **高度可定制**：用户可以提供自己的单词列表（例如星球、颜色、元素等）来替换默认的动物列表。

## 3. 安装指南

目前，`AnimalID` 作为一个本地库，你可以将 `animalid` 文件夹直接放置在你的项目根目录下。

项目结构建议如下：

```
your_project/
├── animalid/
│   ├── __init__.py
│   └── generator.py
├── your_app.py
└── ...
```

然后，你就可以在你的代码中通过 `from animalid import AnimalIdGenerator` 来使用它。

## 4. 快速入门

以下是一个最简单的示例，展示了 `AnimalID` 的核心功能。

```python
from animalid import AnimalIdGenerator

# 1. 使用一个秘密密钥初始化生成器
#    重要：请从安全的地方（如环境变量）加载密钥，不要硬编码！
SECRET_KEY = "a-very-secret-and-long-key"
id_generator = AnimalIdGenerator(secret_key=SECRET_KEY)

# 2. 生成一个新的 AnimalID
new_id = id_generator.generate()
print(f"生成的新ID: {new_id}")
# 输出示例: 生成的新ID: bee-sloth-auk-mole

# 3. 校验这个ID的有效性
is_valid = id_generator.verify(new_id)
print(f"ID '{new_id}' 是否有效? {is_valid}")
# 输出: ID 'bee-sloth-auk-mole' 是否有效? True

# 4. 尝试校验一个被篡改的ID
tampered_id = "bee-sloth-auk-cat" # 将校验和 'mole' 改为 'cat'
is_valid_tampered = id_generator.verify(tampered_id)
print(f"被篡改的ID '{tampered_id}' 是否有效? {is_valid_tampered}")
# 输出: 被篡改的ID 'bee-sloth-auk-cat' 是否有效? False
```

## 5. 详细用法

### 5.1 初始化生成器

在使用任何功能之前，你必须创建一个 `AnimalIdGenerator` 的实例。

```python
from animalid import AnimalIdGenerator

# 必须提供一个非空的字符串作为 secret_key
generator = AnimalIdGenerator(secret_key="your-production-secret-key")
```

构造函数 `__init__(self, secret_key: str, animal_list: tuple = ANIMAL_LIST)` 接受两个参数：
*   `secret_key` (str): **必需**。用于哈希计算的密钥，是保证ID安全的核心。
*   `animal_list` (tuple/list): **可选**。一个包含单词的元组或列表。如果未提供，将使用内置的动物列表。

### 5.2 生成ID

使用 `generate()` 方法来创建一个新的、有效的 `AnimalID`。

```python
new_id = generator.generate()
# new_id -> "yak-crow-asp-rhino" (示例)
```

### 5.3 校验ID

使用 `verify(animal_id)` 方法来检查一个ID是否有效。它会执行以下检查：
1.  格式是否为 `a-b-c-d`。
2.  ID中的所有单词是否存在于词库中。
3.  根据前三个单词和密钥重新计算的校验和是否与第四个单词匹配。

```python
# 校验一个有效的ID
result = generator.verify("yak-crow-asp-rhino")
print(result) # -> True

# 校验一个无效的ID（校验和错误）
result = generator.verify("yak-crow-asp-dog")
print(result) # -> False

# 校验一个格式错误的ID
result = generator.verify("yak-crow-asp")
print(result) # -> False

# 使用不同密钥的生成器进行校验，也会失败
wrong_key_generator = AnimalIdGenerator(secret_key="another-key")
result = wrong_key_generator.verify("yak-crow-asp-rhino")
print(result) # -> False
```

### 5.4 使用装饰器自动注入ID

为了方便地为函数调用（例如处理API请求）分配唯一ID，你可以使用装饰器。

```python
# 1. 从你的生成器实例获取装饰器
assign_id = generator.get_decorator()

# 2. 将它应用到你的函数上
@assign_id
def process_payment(order_details, animal_id=None):
    """
    处理支付请求。animal_id 会被自动生成并注入。
    """
    print(f"开始处理支付，追踪ID: {animal_id}")
    # ... 业务逻辑 ...
    print(f"支付处理完成，ID: {animal_id}")

# 3. 正常调用你的函数，无需手动传入ID
process_payment(order_details={"item": "Laptop", "amount": 1200})
```

每次调用 `process_payment` 时，一个新的、有效的 `AnimalID` 都会被生成，并通过 `animal_id` 关键字参数传递给该函数。

### 5.5 使用自定义词库

你可以轻松地将动物列表替换为任何你想要的单词列表。

```python
PLANET_LIST = ("mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune")

planet_id_generator = AnimalIdGenerator(
    secret_key="my-space-secret",
    animal_list=PLANET_LIST
)

new_planet_id = planet_id_generator.generate()
print(new_planet_id)
# 输出示例: "saturn-venus-mars-uranus"
```

## 6. 工作原理：校验和

`AnimalID` 的安全性与可靠性来自于其校验和的计算方式。这个过程可以分解为以下几步：

1.  **拼接**: 将ID的前三个部分（例如 `"yak-crow-asp"`）与你的 `secret_key` 拼接起来，中间用一个分隔符隔开。
    *   `"yak-crow-asp:your-production-secret-key"`

2.  **哈希**: 对这个拼接后的字符串使用一个标准的、安全的哈希算法（`SHA-256`）进行计算，得到一个长长的、唯一的哈希值。
    *   `sha256("...") -> "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"`

3.  **转换**: 将这个十六进制的哈希值转换成一个巨大的整数。

4.  **取模**: 用这个巨大的整数对你的词库长度（例如，内置动物列表长度为88）进行取模（`%`）运算。结果是一个介于 `0` 和 `87` 之间的数字。
    *   `big_integer % 88 -> 65`

5.  **映射**: 这个数字就是校验和单词在词库中的索引。
    *   `ANIMAL_LIST[65] -> "rhino"`

因为 `secret_key` 的参与，不知道密钥的攻击者无法计算出正确的校验和，从而无法伪造一个有效的ID。

## 7. API 参考

### Class `AnimalIdGenerator`

```python
AnimalIdGenerator(secret_key: str, animal_list: tuple = ANIMAL_LIST)
```
*   **`secret_key`**: `str` - 用于签名和验证的秘密密钥。
*   **`animal_list`**: `tuple` or `list` - 用于生成ID的单词列表。默认为内置的 `ANIMAL_LIST`。

#### Methods

*   **`generate() -> str`**
    *   生成一个全新的、带校验和的 `AnimalID` 字符串。
    *   **返回**: `str` - 格式为 `"a-b-c-d"` 的ID。

*   **`verify(animal_id: str) -> bool`**
    *   校验一个给定的 `animal_id` 是否有效。
    *   **参数**: `animal_id` (`str`) - 需要被校验的ID。
    *   **返回**: `bool` - 如果ID有效则为 `True`，否则为 `False`。

*   **`get_decorator() -> callable`**
    *   返回一个Python装饰器。该装饰器会为被装饰的函数自动生成并注入一个 `animal_id` 关键字参数。
    *   **返回**: `callable` - 一个装饰器函数。

## 8. 安全注意事项

**`secret_key` 的管理是本库安全性的核心！**

*   **绝对不要** 将 `secret_key` 硬编码在你的源代码中。这会使你的密钥暴露在版本控制系统（如 Git）中。
*   **推荐做法** 是通过**环境变量**来加载密钥。
    ```python
    import os
    
    SECRET_KEY = os.getenv("ANIMALID_SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("ANIMALID_SECRET_KEY 环境变量未设置！")
    
    id_generator = AnimalIdGenerator(secret_key=SECRET_KEY)
    ```
*   确保你的 `secret_key` 足够长且难以猜测，以增加安全性。
*   如果密钥泄露，所有之前生成的ID都将面临被伪造的风险。你需要立即更换密钥。