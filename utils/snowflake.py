"""
雪花算法 ID 生成器
=================

Twitter Snowflake 算法的 Python 实现。

64位结构:
┌─┬───────────────────────────────────────────┬──────────┬────────────┐
│0│              41位 时间戳(毫秒)             │ 10位机器  │ 12位序列号  │
└─┴───────────────────────────────────────────┴──────────┴────────────┘

特性:
  - 全局唯一（分布式环境不冲突）
  - 趋势递增（利于数据库 B+Tree 索引）
  - 纯本地生成（不依赖数据库，零网络开销）
  - 高性能（单机每秒可生成 409.6 万个 ID

使用方式:
    sf = SnowflakeGenerator(worker_id=1, datacenter_id=1)
    unique_id = sf.next_id()           # → 7382910472839168
    order_no = sf.next_order_no()      # → ORD202605040001
    product_no = sf.next_product_no()  # → PROD202605040001
"""

import time
import threading
from datetime import datetime


class SnowflakeGenerator:
    """
    雪花算法 ID 生成器

    参数:
        worker_id:     工作机器 ID (0~31), 默认 1
        datacenter_id: 数据中心 ID (0~31), 默认 1
        epoch:         起始时间戳(毫秒), 默认 2024-01-01 00:00:00
    """

    def __init__(self, worker_id: int = 1, datacenter_id: int = 1, epoch: int = None):
        # 位数分配
        self._worker_id_bits = 5
        self._datacenter_id_bits = 5
        self._sequence_bits = 12

        # 最大值校验
        max_worker_id = -1 ^ (-1 << self._worker_id_bits)       # 31
        max_datacenter_id = -1 ^ (-1 << self._datacenter_id_bits)  # 31

        if worker_id < 0 or worker_id > max_worker_id:
            raise ValueError(f"worker_id 必须在 0~{max_worker_id} 之间")
        if datacenter_id < 0 or datacenter_id > max_datacenter_id:
            raise ValueError(f"datacenter_id 必须在 0~{max_datacenter_id} 之间")

        self._worker_id = worker_id
        self._datacenter_id = datacenter_id
        self._sequence = 0
        self._last_timestamp = -1

        # 起始时间戳: 2024-01-01 00:00:00 (毫秒)
        # 减小 epoch 可以让 41 位时间戳用更久 (约 69 年)
        self._epoch = epoch or int(datetime(2024, 1, 1, 0, 0, 0).timestamp() * 1000)

        # 位移量
        self._worker_id_shift = self._sequence_bits                              # 12
        self._datacenter_id_shift = self._sequence_bits + self._worker_id_bits   # 17
        self._timestamp_shift = self._sequence_bits + self._worker_id_bits + self._datacenter_id_bits  # 22

        # 序列号掩码
        self._sequence_mask = -1 ^ (-1 << self._sequence_bits)  # 4095

        # 线程锁 (保证多线程安全)
        self._lock = threading.Lock()

    def _current_millis(self) -> int:
        """获取当前毫秒时间戳"""
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp: int) -> int:
        """
        等待到下一毫秒
        当同一毫秒内序列号用完时调用
        """
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_millis()
        return timestamp

    def next_id(self) -> int:
        """
        生成下一个唯一 ID

        Returns:
            int: 64 位唯一 ID

        工作原理:
            1. 获取当前毫秒时间戳
            2. 如果和上次相同 → 序列号+1
            3. 序列号用完(>4095) → 等到下一毫秒
            4. 如果时间回拨 → 抛出异常 (防止生成重复ID)
            5. 组装: 时间戳 << 22 | 数据中心 << 17 | 机器 << 12 | 序列号
        """
        with self._lock:
            timestamp = self._current_millis()

            # 时钟回拨检测 (工业级关键保护!)
            if timestamp < self._last_timestamp:
                offset = self._last_timestamp - timestamp
                raise RuntimeError(
                    f"系统时钟回拨 {offset} 毫秒, 拒绝生成 ID 防止重复"
                )

            # 同一毫秒内
            if timestamp == self._last_timestamp:
                self._sequence = (self._sequence + 1) & self._sequence_mask
                # 序列号用完, 等到下一毫秒
                if self._sequence == 0:
                    timestamp = self._wait_next_millis(self._last_timestamp)
            else:
                # 新的一毫秒, 序列号归零
                self._sequence = 0

            self._last_timestamp = timestamp

            # 组装 64 位 ID
            unique_id = (
                ((timestamp - self._epoch) << self._timestamp_shift)
                | (self._datacenter_id << self._datacenter_id_shift)
                | (self._worker_id << self._worker_id_shift)
                | self._sequence
            )

            return unique_id

    # ======================================================================
    # 业务编号生成 (编号 = 前缀 + 日期 + 序列号)
    # ======================================================================

    def next_order_no(self) -> str:
        """
        生成订单编号

        格式: ORD + YYYYMMDD + 6位序列号
        例:   ORD20260504000001
        """
        date_str = datetime.now().strftime("%Y%m%d")
        seq = self.next_id() % 1000000  # 取低 6 位
        return f"ORD{date_str}{seq:06d}"

    def next_product_no(self) -> str:
        """
        生成商品编号

        格式: PROD + YYYYMMDD + 6位序列号
        例:   PROD20260504000001
        """
        date_str = datetime.now().strftime("%Y%m%d")
        seq = self.next_id() % 1000000
        return f"PROD{date_str}{seq:06d}"


# ======================================================================
# 全局单例 (整个系统共享一个生成器实例)
# ======================================================================
# 单机部署时 worker_id=1, datacenter_id=1
# 多机部署时通过环境变量区分:
#   SNOWFLAKE_WORKER_ID=1
#   SNOWFLAKE_DATACENTER_ID=1

import os

_DEFAULT_WORKER_ID = int(os.getenv("SNOWFLAKE_WORKER_ID", "1"))
_DEFAULT_DATACENTER_ID = int(os.getenv("SNOWFLAKE_DATACENTER_ID", "1"))

snowflake = SnowflakeGenerator(
    worker_id=_DEFAULT_WORKER_ID,
    datacenter_id=_DEFAULT_DATACENTER_ID
)