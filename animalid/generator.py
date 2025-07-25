# animalid/generator.py

import random
import hashlib
from functools import wraps

# 内置一个足够大的动物列表，确保随机性和低碰撞率
# 使用元组使其不可变
ANIMAL_LIST = (
    "ant", "ape", "asp", "auk", "bat", "bear", "bee", "bird", "boar", "bug",
    "cat", "cod", "cow", "crab", "crow", "cub", "deer", "dog", "dove", "duck",
    "eel", "elk", "emu", "ewe", "finch", "fish", "flea", "fly", "fox", "frog",
    "gecko", "goat", "gull", "hare", "hawk", "hen", "hog", "ibex", "ibis", "jay",
    "kiwi", "koala", "lark", "lion", "lynx", "mink", "mole", "moth", "mouse", "mule",
    "newt", "owl", "ox", "panda", "parrot", "pig", "pike", "puma", "pup", "python",
    "quail", "rabbit", "rat", "raven", "rhino", "roc", "rook", "salmon", "seal", "shark",
    "sheep", "shrew", "skunk", "sloth", "snake", "spider", "swan", "swift", "tapir", "teal",
    "tiger", "toad", "trout", "tuna", "turkey", "viper", "vole", "wasp", "whale", "wolf",
    "worm", "wren", "yak", "zebra"
)


class AnimalIdGenerator:
    """
    一个用于生成和校验带校验和的动物ID的类。

    ID 格式: "animal1-animal2-animal3-checksum_animal"
    第四个动物是基于前三个和 secret_key 计算出的校验和，
    这可以防止ID被轻易伪造。
    """

    def __init__(self, secret_key: str, animal_list: tuple = ANIMAL_LIST):
        """
        初始化生成器。

        :param secret_key: 一个用于哈希计算的密钥。必须提供，且不能为空。
                           这是保证ID安全性的核心。
        :param animal_list: 一个包含动物名称的元组或列表。默认为内置列表。
        """
        if not secret_key or not isinstance(secret_key, str):
            raise ValueError("secret_key 必须是一个非空字符串。")
        if not animal_list or len(animal_list) < 10:
            raise ValueError("animal_list 必须至少包含10个元素。")

        self.secret_key = secret_key
        self.animal_list = tuple(animal_list)
        self.animal_set = set(self.animal_list) # 用于快速查找
        self.list_len = len(self.animal_list)

    def _calculate_checksum_animal(self, base_id: str) -> str:
        """
        根据基础ID和密钥计算校验和动物。
        这是一个内部方法。
        """
        # 1. 准备用于哈希的字符串，包含基础ID和密钥
        string_to_hash = f"{base_id}:{self.secret_key}"

        # 2. 使用SHA-256进行哈希计算
        hasher = hashlib.sha256(string_to_hash.encode('utf-8'))
        hex_digest = hasher.hexdigest()

        # 3. 将哈希结果（一个很长的十六进制数）转换为整数
        hash_int = int(hex_digest, 16)

        # 4. 使用模运算，将其映射到动物列表的索引上
        checksum_index = hash_int % self.list_len

        # 5. 返回对应的动物名
        return self.animal_list[checksum_index]

    def generate(self) -> str:
        """
        生成一个新的、带校验和的 animal ID。

        :return: 一个格式为 "a-b-c-d" 的字符串ID。
        """
        # 1. 随机选择3个不重复的动物作为基础
        base_animals = random.sample(self.animal_list, 3)
        base_id = "-".join(base_animals)

        # 2. 计算校验和动物
        checksum_animal = self._calculate_checksum_animal(base_id)

        # 3. 组合成最终的ID
        final_id = f"{base_id}-{checksum_animal}"
        return final_id

    def verify(self, animal_id: str) -> bool:
        """
        校验一个 animal ID 是否有效。

        校验过程:
        1. 检查格式是否正确。
        2. 检查所有部分是否都是已知的动物。
        3. 重新计算校验和并与ID中提供的进行比较。

        :param animal_id: 需要被校验的ID字符串。
        :return: 如果ID有效则返回 True，否则返回 False。
        """
        parts = animal_id.split('-')

        # 1. 检查格式：必须由4个部分组成
        if len(parts) != 4:
            return False

        # 2. 检查所有部分是否都是列表中的动物
        if not all(p in self.animal_set for p in parts):
            return False

        # 3. 重新计算校验和并比较
        base_id = "-".join(parts[:3])
        provided_checksum_animal = parts[3]

        expected_checksum_animal = self._calculate_checksum_animal(base_id)

        return provided_checksum_animal == expected_checksum_animal

    def get_decorator(self):
        """
        返回一个装饰器，该装饰器会自动为被装饰的函数注入 'animal_id'。
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成一个新的ID
                new_id = self.generate()
                print(f"--- [AnimalID] 为函数 '{func.__name__}' 分配ID: {new_id} ---")
                # 将ID作为关键字参数注入
                return func(*args, animal_id=new_id, **kwargs)
            return wrapper
        return decorator

